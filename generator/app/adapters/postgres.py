from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import RootModel

from app.core.db import PromptsRepository
from app.core.models import Prompt, Plan

STMT_GET_PROMPTS_FOR_PROJECT = text(
    "SELECT "
    "   id, "
    "   text, "
    "   base, "
    "   patches, "
    "   status, "
    "   dt_created, "
    "   dt_done "
    "FROM "
    "   generator.prompts "
    "WHERE "
    "   project_id = :project_id "
    "   AND NOT deleted "
    "ORDER BY "
    "   dt_created"
)
STMT_SAVE_PROMPT = text(
    "INSERT INTO generator.prompts("
    "   id, "
    "   project_id, "
    "   text, "
    "   base, "
    "   patches, "
    "   status, "
    "   dt_created, "
    "   dt_done "
    ") "
    "VALUES ( "
    "   :id, "
    "   :project_id, "
    "   :text, "
    "   :base, "
    "   :patches, "
    "   :status, "
    "   :dt_created, "
    "   :dt_done "
    ") "
    "ON CONFLICT (id) DO UPDATE SET "
    "   project_id = excluded.project_id, "
    "   text = excluded.text, "
    "   base = excluded.base, "
    "   patches = excluded.patches, "
    "   status = excluded.status, "
    "   dt_created = excluded.dt_created, "
    "   dt_done = excluded.dt_done"
).bindparams(bindparam("base", type_=JSONB), bindparam("patches", type_=JSONB))
STMT_DELETE_PROMPT = text(
    "UPDATE "
    "   generator.prompts "
    "SET "
    "   deleted = true "
    "WHERE "
    "   id = :prompt_id"
)
STMT_GET_PROMPT = text(
    "SELECT "
    "   project_id, "
    "   text, "
    "   base, "
    "   patches, "
    "   status, "
    "   dt_created, "
    "   dt_done "
    "FROM "
    "   generator.prompts "
    "WHERE "
    "   id = :prompt_id "
    "   AND NOT deleted"
)


class PostgresPromptsRepository(PromptsRepository):
    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def get_for_project(self, project_id: str) -> list[Prompt]:
        async with self.engine.connect() as conn:
            cursor = await conn.execute(
                STMT_GET_PROMPTS_FOR_PROJECT, {"project_id": project_id}
            )
            prompts = [
                Prompt(
                    id=row[0],
                    project_id=project_id,
                    text=row[1],
                    base=Plan.Content.model_validate(row[2]),
                    patches=RootModel[list[Plan.Patch]].model_validate(row[3]).root,
                    status=row[4],
                    dt_created=row[5],
                    dt_done=row[6],
                )
                for row in cursor.all()
            ]
            return prompts

    async def save(self, prompt: Prompt) -> None:
        async with self.engine.connect() as conn:
            _ = await conn.execute(
                STMT_SAVE_PROMPT,
                prompt.model_dump(),
            )
            await conn.commit()

    async def get(self, prompt_id: str) -> Prompt | None:
        async with self.engine.connect() as conn:
            cursor = await conn.execute(STMT_GET_PROMPT, {"prompt_id": prompt_id})
            row = cursor.one_or_none()
            if not row:
                return None
            return Prompt(
                id=prompt_id,
                project_id=row[0],
                text=row[1],
                base=Plan.Content.model_validate(row[2]),
                patches=RootModel[list[Plan.Patch]].model_validate(row[3]).root,
                status=row[4],
                dt_created=row[5],
                dt_done=row[6],
            )

    async def delete(self, prompt_id: str) -> None:
        async with self.engine.connect() as conn:
            _ = await conn.execute(
                STMT_DELETE_PROMPT,
                {"prompt_id": prompt_id},
            )
            await conn.commit()
