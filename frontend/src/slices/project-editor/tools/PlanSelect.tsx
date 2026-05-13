import { useNavigate } from "react-router";
import { Button } from "../../../shared/components/button/Button";
import { ContextMenu } from "../../../shared/components/context-menu/ContextMenu";
import { ContextMenuOption } from "../../../shared/components/context-menu/ContextMenuOption";
import {
  useCreatePlanMutation,
  useGetAllPlansInProjectQuery,
  usePatchProjectMutation,
} from "../../api/slice";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { notify } from "../../notifications/slice";
import { projectSaved, selectProjectEditor } from "../slice";

export function PlanSelect({
  projectId,
  projectOwned,
}: {
  projectId: string;
  projectOwned: boolean;
}) {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const editor = useAppSelector(selectProjectEditor);
  const { data: plans } = useGetAllPlansInProjectQuery(projectId);
  const [patchProject] = usePatchProjectMutation();
  const [createPlan, { isLoading: isCreatingPlan }] = useCreatePlanMutation();

  async function handleAddPlan() {
    try {
      if (editor.project) {
        const revision = await patchProject({
          id: editor.project.id,
          revision: editor.project.revision,
          patch: editor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(projectSaved(revision));
      }
      const plan = await createPlan(projectId).unwrap();
      navigate(`/editor/project/${projectId}/plan/${plan.id}`);
    } catch {
      dispatch(
        notify({
          text: "Failed to create a plan",
          severity: "error",
        }),
      );
    }
  }

  return (
    <ContextMenu
      content={
        <>
          {projectOwned && (
            <ContextMenuOption
              text="Add plan"
              icon="plus.png"
              onClick={handleAddPlan}
              loading={isCreatingPlan}
            />
          )}
          {plans &&
            plans.map((plan, idx) => (
              <ContextMenuOption
                key={plan.id}
                text={`${idx + 1}. ` + (plan.name || "Untitled plan")}
                onClick={() =>
                  navigate(`/editor/project/${projectId}/plan/${plan.id}`)
                }
              />
            ))}
        </>
      }
    >
      <Button icon="room.png" />
    </ContextMenu>
  );
}
