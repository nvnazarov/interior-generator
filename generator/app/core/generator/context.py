from openai import AsyncOpenAI
import logging
from uuid import uuid4

from app.core.models import Plan, Project
from app.core.facade import SystemFacade
from app.core.generator.scene import (
    SceneGraph,
    OnFloor,
    OnTopOf,
    InFrontOf,
    AgainstWall,
    FarWall,
    FaceToFace,
    BackToBack,
    SideBySide,
    SceneObject,
)
from app.core.generator.prompts import (
    SPATIAL_ANALYSIS_PROMPT,
    SPATIAL_RELATIONSHIP_PROMPT,
    IDENTIFY_ACTIONS_PROMPT,
)

logger = logging.getLogger(__name__)


def semantic_suffix(index: int) -> str:
    if index < 0:
        raise ValueError("index cannot be less than 0")
    return "-" + (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[index] if index < 26 else uuid4().hex[:6]
    )


def strip_list(list_: list[str]) -> list[str]:
    return list(map(lambda e: e.strip(), list_))


class GenerationContext:
    def __init__(
        self,
        ai: AsyncOpenAI,
        facade: SystemFacade,
        text: str,
        count: int,
        project: Project,
        base_plan: Plan | None,
    ):
        self.ai = ai
        self.facade = facade
        self.text = text
        self.count = count
        self.project = project
        self.base_plan = base_plan
        self.scene = SceneGraph(project)

    async def generate_patches(self) -> list[Plan.Patch]:
        """
        Pipeline:
        1. Generate description of the existing project.
        2. Analyze spatial relations in user's request using LLM and form a
           better prompt that captures these relations.
        3. Analyze specific constraints in the new prompt and build a relations graph.
        4. Traverse the graph in order and place objects according to
           the constraints. Do it several times to produce different plans, or use a
           sophisticated GA.
        5. Return the best plans from the generated plans.
        """

        # Add existing furniture to the scene graph.
        if self.base_plan:
            name_counts = dict[str, int]()
            for plan_furniture in self.base_plan.content.furniture.values():
                furniture = await self.facade.find_furniture(
                    plan_furniture.furniture_id
                )
                if not furniture:
                    logger.warning(
                        {"msg": "furniture not found", "id": plan_furniture.id}
                    )
                    continue
                object = self.scene.get_or_create_object(plan_furniture.id)
                object.add_choice(furniture)
                object.lock_at_location(
                    plan_furniture.x,
                    plan_furniture.y,
                    plan_furniture.z,
                    plan_furniture.yaw,
                )
                count = name_counts.get(furniture.name, 0)
                object.set_semantic_name(furniture.name + semantic_suffix(count))
                name_counts[furniture.name] = count + 1
        base_scene_description = self.scene.describe()
        logger.debug({"msg": "built base scene", "description": base_scene_description})

        # Identify which objects should be removed or moved. Record this
        # information in scene graph.
        await self._identify_furniture_actions(base_scene_description, self.text)

        # Analyze spatial relations.
        spatial_relations_description = await self._describe_spatial_relations(
            base_scene_description, self.text
        )
        await self._parse_furniture_and_relations(spatial_relations_description)

        patches = list[Plan.Patch]()
        for _ in range(self.count):
            self.scene.rearrange()
            patches.append(self.scene.as_patch_to(self.base_plan))

        logger.debug(
            {"msg": "generated patches", "patches": [p.model_dump() for p in patches]}
        )

        return patches

    async def _parse_furniture_and_relations(self, spatial_relations_description: str):
        completion = await self.ai.chat.completions.create(
            model="google/gemma-4-31b-it",
            messages=[
                {
                    "role": "user",
                    "content": SPATIAL_RELATIONSHIP_PROMPT.format(
                        spatial_relations_description
                    ),
                },
            ],
        )
        choice = completion.choices[0]
        if choice.finish_reason != "stop":
            logger.warning(
                {
                    "msg": "llm stopped generation unnaturally",
                    "finish_reason": choice.finish_reason,
                }
            )
        if choice.message.content is None:
            logger.error({"msg": "llm did not generate any content"})
            raise RuntimeError("failed to generate relations graph")
        logger.debug(
            {"msg": "llm generated constraints", "content": choice.message.content}
        )
        raw_relations = choice.message.content.split("\n")
        new_objects = list[SceneObject]()
        for raw_relation in raw_relations:
            constraints = raw_relation.split("|")
            if len(constraints) == 0:
                logger.warning(
                    {
                        "msg": "generated relation is invalid",
                        "raw_relation": raw_relation,
                    }
                )
                continue
            semantic_name = constraints[0].strip()

            def get_or_create(name: str) -> SceneObject:
                object, existed = self.scene.get_or_create_object_by_semantic_name(name)
                if not existed:
                    new_objects.append(object)
                return object

            object = get_or_create(semantic_name)
            for constraint in constraints[1:]:
                constraint = constraint.strip()
                match constraint:
                    case "on floor":
                        self.scene.add_constraint(OnFloor(object.id))
                        continue
                    case "against wall":
                        self.scene.add_constraint(AgainstWall(object.id))
                        continue
                    case "far wall":
                        self.scene.add_constraint(FarWall(object.id))
                        continue
                    case _:
                        pass
                parts = strip_list(constraint.split(","))
                match parts:
                    case [semantic_name, "on top"]:
                        bottom_object = get_or_create(semantic_name)
                        self.scene.add_constraint(OnTopOf(bottom_object.id, object.id))
                    case [semantic_name, "in front of"]:
                        other = get_or_create(semantic_name)
                        self.scene.add_constraint(InFrontOf(object.id, other.id))
                    case [semantic_name, "face to face"]:
                        other = get_or_create(semantic_name)
                        self.scene.add_constraint(FaceToFace(object.id, other.id))
                    case [semantic_name, "back to back"]:
                        other = get_or_create(semantic_name)
                        self.scene.add_constraint(BackToBack(object.id, other.id))
                    case [semantic_name, "side by side"]:
                        other = get_or_create(semantic_name)
                        self.scene.add_constraint(SideBySide(object.id, other.id))
                    # TODO: other constraints
                    case _:
                        logger.warning(
                            {
                                "msg": "generated constraint is invalid",
                                "raw": constraint,
                            }
                        )
                        continue

        # For the new objects, add appropriate furniture choices.
        # TODO: generate descriptions for these objects and use them to
        # search appropriate furniture in the catalog.
        logger.info({"msg": "new objects", "count": len(new_objects)})
        for object in new_objects:
            if not object.semantic_name:
                # TODO
                logger.warning({"msg": "no furniture choices", "object": object.id})
                continue
            furniture_choices = await self.facade.match_furniture(
                object.semantic_name, 3
            )
            if len(furniture_choices) == 0:
                logger.warning(
                    {
                        "msg": "no furniture choices",
                        "semantic_name": object.semantic_name,
                    }
                )
                continue
            object.add_choices(furniture_choices)

    async def _describe_spatial_relations(
        self, scene_description: str, user_instruction: str
    ) -> str:
        completion = await self.ai.chat.completions.create(
            model="google/gemma-4-31b-it",
            messages=[
                {"role": "system", "content": SPATIAL_ANALYSIS_PROMPT},
                {
                    "role": "user",
                    "content": f"Apartment: {scene_description}\nInstruction: {user_instruction}",
                },
            ],
        )
        choice = completion.choices[0]
        if choice.finish_reason != "stop":
            logger.warning(
                {
                    "msg": "llm stopped generation unnaturally",
                    "finish_reason": choice.finish_reason,
                }
            )
        if choice.message.content is None:
            logger.warning({"msg": "llm did not generate any content"})
        logger.debug(
            {"msg": "performed spatial analysis", "content": choice.message.content}
        )
        return choice.message.content or user_instruction

    async def _identify_furniture_actions(
        self, scene_description: str, instruction: str
    ):
        completion = await self.ai.chat.completions.create(
            model="google/gemma-4-31b-it",
            messages=[
                {"role": "system", "content": IDENTIFY_ACTIONS_PROMPT},
                {
                    "role": "user",
                    "content": f"Apartment: {scene_description}\nInstruction: {instruction}",
                },
            ],
        )
        choice = completion.choices[0]
        if choice.finish_reason != "stop":
            logger.warning(
                {
                    "msg": "llm stopped generation unnaturally",
                    "finish_reason": choice.finish_reason,
                }
            )
        if choice.message.content is None:
            logger.warning({"msg": "llm did not generate any content"})
            return
        lines = choice.message.content.split("\n")
        match lines:
            case [removed, moved]:
                removed = removed.removeprefix("removed:")
                moved = moved.removeprefix("moved:")
                for semantic_name in removed.split(","):
                    semantic_name = semantic_name.strip()
                    object = self.scene.find_object_by_semantic_name(semantic_name)
                    if object is not None:
                        object.mark_removed()
                for semantic_name in moved.split(","):
                    semantic_name = semantic_name.strip()
                    object = self.scene.find_object_by_semantic_name(semantic_name)
                    if object is not None:
                        object.unlock_location()
            case _:
                logger.warning(
                    {"msg": "invalid actions", "content": choice.message.content}
                )
