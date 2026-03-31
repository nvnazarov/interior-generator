import { useCallback } from "react";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import { Button } from "./Button";
import { useNavigate } from "react-router";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import {
  useCreatePlanMutation,
  useDeletePlanMutation,
  useGetAllPlansInProjectQuery,
  usePatchPlanMutation,
} from "../api/slice";
import { planSaved, selectPlanEditor } from "./slice";
import { UrlUtil } from "../../shared/util";
import { Config } from "../../shared/config";

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
  const [deletePlan] = useDeletePlanMutation();
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
          name: "Edit project",
          onClick: async () => {
            if (editor.plan) {
              navigate(`/editor/project/${editor.plan.projectId}`);
            }
          },
        },
        {
          divider: true,
        },
        {
          name: "Export (DXF)",
          onClick: async () => {
            if (editor.plan) {
              const resp = await fetch(
                `${UrlUtil.noRightSlash(Config.gateway.baseUrl)}/api/plans/${editor.plan.id}/export/dxf`,
                {
                  method: "POST",
                  body: "{}",
                  headers: { "Content-Type": "application/json" },
                },
              );
              if (!resp.ok) {
                throw new Error("error: export plan dxf: response is not ok");
              }
              const blob = await resp.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `${editor.plan.id}.dxf`;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
            }
          },
        },
        {
          name: "Delete plan",
          onClick: async () => {
            if (editor.plan) {
              await deletePlan(planId).unwrap();
              navigate(`/editor/project/${projectId}`);
            }
          },
        },
        {
          name: "Create plan",
          onClick: async () => {
            if (editor.plan) {
              const plan = await createPlan(projectId).unwrap();
              navigate(`/editor/project/${projectId}/plan/${plan.id}`);
            }
          },
        },
        {
          divider: true,
        },
        ...(data || []).map((plan) => ({
          name: plan.name || "Untitiled plan",
          onClick: () =>
            navigate(`/editor/project/${projectId}/plan/${plan.id}`),
        })),
      ],
    });
  }, [menu, editor, projectId, planId, dispatch]);

  return (
    <Button icon="menu.png" onClick={handleClick} disabled={!editor.plan} />
  );
}
