import { useCallback } from "react";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import { Button } from "./Button";
import { useNavigate } from "react-router";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import {
  useCreatePlanMutation,
  useDeleteProjectMutation,
  useGetAllPlansInProjectQuery,
  usePatchProjectMutation,
} from "../api/slice";
import { projectSaved, selectProjectEditor } from "./slice";

export function MenuButton({ projectId }: { projectId: string }) {
  const dispatch = useAppDispatch();
  const menu = useContextMenu();
  const editor = useAppSelector(selectProjectEditor);
  const navigate = useNavigate();
  const [patchProject] = usePatchProjectMutation();
  const [createPlan] = useCreatePlanMutation();
  const [deleteProject] = useDeleteProjectMutation();
  const { data } = useGetAllPlansInProjectQuery(projectId);

  const handleClick = useCallback(() => {
    if (!editor.project) {
      return;
    }
    menu.show({
      x: 10,
      y: 70,
      items: [
        {
          name: "Save & Exit",
          onClick: async () => {
            if (editor.project) {
              const revision = await patchProject({
                id: editor.project.id,
                revision: editor.project.revision,
                patch: editor.unsavedAccumulatedPatch,
              }).unwrap();
              dispatch(projectSaved(revision));
            }
            navigate("/");
          },
        },
        {
          name: "Delete project",
          onClick: async () => {
            if (editor.project) {
              await deleteProject(editor.project.id).unwrap();
              navigate("/");
            }
          },
        },
        {
          name: "Create plan",
          onClick: async () => {
            if (editor.project) {
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
  }, [menu, editor, projectId, dispatch]);

  return (
    <Button icon="menu.png" onClick={handleClick} disabled={!editor.project} />
  );
}
