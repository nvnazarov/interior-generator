import { useNavigate } from "react-router";
import { Button } from "../../../shared/components/button/Button";
import { ContextMenu } from "../../../shared/components/context-menu/ContextMenu";
import { ContextMenuOption } from "../../../shared/components/context-menu/ContextMenuOption";
import {
  useCreatePlanMutation,
  useGetAllPlansInProjectQuery,
} from "../../api/slice";

export function PlanSelect({ projectId }: { projectId: string }) {
  const navigate = useNavigate();
  const { data: plans } = useGetAllPlansInProjectQuery(projectId);
  const [createPlan, { isLoading: isCreatingPlan }] = useCreatePlanMutation();

  async function handleAddPlan() {
    const plan = await createPlan(projectId).unwrap();
    navigate(`/editor/project/${projectId}/plan/${plan.id}`);
  }

  return (
    <ContextMenu
      content={
        <>
          <ContextMenuOption
            text="Add plan"
            icon="plus.png"
            onClick={handleAddPlan}
            loading={isCreatingPlan}
          />
          <ContextMenuOption
            text="Project"
            onClick={() => navigate(`/editor/project/${projectId}`)}
            loading={isCreatingPlan}
          />
          {plans &&
            plans.map((plan, idx) => (
              <ContextMenuOption
                key={plan.id}
                text={`${idx}. ` + (plan.name || "Untitled plan")}
                onClick={() =>
                  navigate(`/editor/project/${projectId}/plan/${plan.id}`)
                }
              />
            ))}
        </>
      }
    >
      <Button text="\/" />
    </ContextMenu>
  );
}
