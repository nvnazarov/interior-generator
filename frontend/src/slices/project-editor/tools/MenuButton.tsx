import { useCallback } from "react";
import { Button } from "../../../shared/components/button/Button";
import { useNavigate } from "react-router";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import {
  useDeleteProjectMutation,
  useGetProjectByIdQuery,
  usePatchProjectMutation,
} from "../../api/slice";
import { projectSaved, selectProjectEditor } from "../slice";
import { Config } from "../../../shared/config";
import { UrlUtil } from "../../../shared/util";
import { ContextMenu } from "../../../shared/components/context-menu/ContextMenu";
import { ContextMenuOption } from "../../../shared/components/context-menu/ContextMenuOption";

export function MenuButton({ projectId }: { projectId: string }) {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const editor = useAppSelector(selectProjectEditor);
  const { data: project, isSuccess: projectLoaded } =
    useGetProjectByIdQuery(projectId);
  const [patchProject] = usePatchProjectMutation();
  const [deleteProject] = useDeleteProjectMutation();

  const handleSaveProjectAndExit = useCallback(async () => {
    if (editor.project) {
      const revision = await patchProject({
        id: editor.project.id,
        revision: editor.project.revision,
        patch: editor.unsavedAccumulatedPatch,
      }).unwrap();
      dispatch(projectSaved(revision));
    }
    navigate("/");
  }, [editor]);

  const handleSaveProject = useCallback(async () => {
    if (editor.project) {
      const revision = await patchProject({
        id: editor.project.id,
        revision: editor.project.revision,
        patch: editor.unsavedAccumulatedPatch,
      }).unwrap();
      dispatch(projectSaved(revision));
    }
  }, [editor]);

  const handleDeleteProject = useCallback(async () => {
    await deleteProject(projectId).unwrap();
    navigate("/");
  }, [projectId]);

  const handleExportProjectToPDF = useCallback(async () => {
    if (!editor.project) {
      return;
    }
    const revision = await patchProject({
      id: editor.project.id,
      revision: editor.project.revision,
      patch: editor.unsavedAccumulatedPatch,
    }).unwrap();
    dispatch(projectSaved(revision));
    const resp = await fetch(
      `${UrlUtil.noRightSlash(Config.gateway.baseUrl)}/api/projects/${editor.project.id}/export/pdf`,
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
    a.download = `${editor.project.id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }, [editor]);

  return (
    <ContextMenu
      content={
        <>
          <ContextMenuOption
            text="Save and exit"
            icon="signout.png"
            onClick={handleSaveProjectAndExit}
          />
          <ContextMenuOption
            text="Save"
            icon="sync.png"
            onClick={handleSaveProject}
          />
          <ContextMenuOption
            text="Delete project"
            icon="trash.png"
            onClick={handleDeleteProject}
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
      <Button icon="menu.png" disabled={!editor.project} />
    </ContextMenu>
  );
}
