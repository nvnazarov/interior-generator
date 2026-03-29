import { useCallback } from "react";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import { Button } from "./Button";
import { useNavigate } from "react-router";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import {
  useCreatePlanMutation,
  useGetAllPlansInProjectQuery,
  usePatchPlanMutation,
} from "../api/slice";
import { planSaved, selectPlanEditor } from "./slice";

export function MenuButton({
  planId,
  projectId,
}: {
  planId: string;
  projectId: string;
}) {
  const dispatch = useAppDispatch();
  const menu = useContextMenu();
  const editor = useAppSelector(selectPlanEditor);
  const navigate = useNavigate();
  const [patchPlan] = usePatchPlanMutation();
  const [createPlan] = useCreatePlanMutation();
  const { data } = useGetAllPlansInProjectQuery(projectId);

  const handleClick = useCallback(() => {
    if (!editor.plan) {
      return;
    }
    menu.show({
      x: 10,
      y: 70,
      items: [
        {
          name: "Save & Exit",
          onClick: async () => {
            if (editor.plan) {
              const revision = await patchPlan({
                id: editor.plan.id,
                revision: editor.plan.revision,
                patch: editor.unsavedAccumulatedPatch,
              }).unwrap();
              dispatch(planSaved(revision));
            }
            navigate("/");
          },
        },
        {
          name: "Create plan",
          onClick: async () => {
            if (editor.plan) {
              const plan = await createPlan(projectId).unwrap();
              navigate(`/projects/${projectId}/plans/${plan.id}`);
            }
          },
        },
        ...(data || []).map((plan) => ({
          name: plan.name || "Untitiled plan",
          onClick: () => navigate(`/projects/${projectId}/plans/${plan.id}`),
        })),
      ],
    });
  }, [menu, editor, projectId, dispatch]);

  return (
    <Button icon="menu.png" onClick={handleClick} disabled={!editor.plan} />
  );
}
