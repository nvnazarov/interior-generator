import { useCallback } from "react";
import { Button } from "../../../shared/components/button/Button";
import { useNavigate } from "react-router";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import {
  useDeletePlanMutation,
  useGetProjectByIdQuery,
  usePatchPlanMutation,
} from "../../api/slice";
import { planSaved, selectPlanEditor } from "../slice";
import { Config } from "../../../shared/config";
import { UrlUtil } from "../../../shared/util";
import { ContextMenu } from "../../../shared/components/context-menu/ContextMenu";
import { ContextMenuOption } from "../../../shared/components/context-menu/ContextMenuOption";

export function MenuButton({ projectId }: { projectId: string }) {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const editor = useAppSelector(selectPlanEditor);
  const { data: project, isSuccess: projectLoaded } =
    useGetProjectByIdQuery(projectId);
  const [patchPlan] = usePatchPlanMutation();
  const [deletePlan] = useDeletePlanMutation();

  const handleSavePlanAndExit = useCallback(async () => {
    if (editor.plan) {
      const revision = await patchPlan({
        id: editor.plan.id,
        revision: editor.plan.revision,
        patch: editor.unsavedAccumulatedPatch,
      }).unwrap();
      dispatch(planSaved(revision));
    }
    navigate("/");
  }, [editor]);

  const handleSavePlan = useCallback(async () => {
    if (editor.plan) {
      const revision = await patchPlan({
        id: editor.plan.id,
        revision: editor.plan.revision,
        patch: editor.unsavedAccumulatedPatch,
      }).unwrap();
      dispatch(planSaved(revision));
    }
  }, [editor]);

  const handleDeletePlan = useCallback(async () => {
    if (editor.plan) {
      await deletePlan(editor.plan.id).unwrap();
    }
    navigate(`/editor/project/${projectId}`);
  }, [editor, projectId]);

  const handleExportProjectToPDF = useCallback(async () => {
    if (!editor.plan) {
      return;
    }
    const revision = await patchPlan({
      id: editor.plan.id,
      revision: editor.plan.revision,
      patch: editor.unsavedAccumulatedPatch,
    }).unwrap();
    dispatch(planSaved(revision));
    const resp = await fetch(
      `${UrlUtil.noRightSlash(Config.gateway.baseUrl)}/api/projects/${projectId}/export/pdf`,
      {
        method: "POST",
        body: "{}",
        headers: { "Content-Type": "application/json" },
      },
    );
    if (!resp.ok) {
      throw new Error("error: export project pdf: response is not ok");
    }
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${projectId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }, [editor, projectId]);

  return (
    <ContextMenu
      content={
        <>
          <ContextMenuOption
            text="Save and exit"
            icon="signout.png"
            onClick={handleSavePlanAndExit}
          />
          <ContextMenuOption
            text="Save"
            icon="sync.png"
            onClick={handleSavePlan}
          />
          <ContextMenuOption
            text="Delete plan"
            icon="trash.png"
            onClick={handleDeletePlan}
          />
          <ContextMenuOption
            text="Export to PDF"
            icon="pdf.png"
            onClick={handleExportProjectToPDF}
          />
          <ContextMenu
            content={
              projectLoaded &&
              (project.published ? (
                <>
                  <ContextMenuOption text="Share" icon="share.png" />
                  <ContextMenuOption text="Copy link" icon="share.png" />
                </>
              ) : (
                <>
                  <ContextMenuOption text="Close" icon="share.png" />
                  <ContextMenuOption text="Copy link" icon="share.png" />
                </>
              ))
            }
            position="right"
          >
            <ContextMenuOption text="Share" icon="share.png" />
          </ContextMenu>
        </>
      }
    >
      <Button icon="menu.png" disabled={!editor.plan} />
    </ContextMenu>
  );
}
