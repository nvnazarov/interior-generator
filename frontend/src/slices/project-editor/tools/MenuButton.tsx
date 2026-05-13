import { useCallback, useState } from "react";
import { Button } from "../../../shared/components/button/Button";
import { useNavigate } from "react-router";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import {
  useDeleteProjectMutation,
  useGetProjectByIdQuery,
  usePatchProjectMutation,
  usePublishProjectMutation,
  useUnpublishProjectMutation,
} from "../../api/slice";
import {
  projectSaved,
  selectProjectEditor,
  type ProjectEditorState,
} from "../slice";
import { Config } from "../../../shared/config";
import { UrlUtil } from "../../../shared/util";
import { ContextMenu } from "../../../shared/components/context-menu/ContextMenu";
import { ContextMenuOption } from "../../../shared/components/context-menu/ContextMenuOption";

function ExportProjectToPDFOption({
  editor,
  projectOwned,
}: {
  editor: ProjectEditorState;
  projectOwned: boolean;
}) {
  const dispatch = useAppDispatch();
  const [exporting, setExporting] = useState(false);
  const [patchProject] = usePatchProjectMutation();

  const handleExportProjectToPDF = useCallback(async () => {
    if (!editor.project) {
      return;
    }
    try {
      setExporting(true);
      if (projectOwned) {
        const revision = await patchProject({
          id: editor.project.id,
          revision: editor.project.revision,
          patch: editor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(projectSaved(revision));
      }
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
    } finally {
      setExporting(false);
    }
  }, [editor]);

  return (
    <ContextMenuOption
      text="Export to PDF"
      icon="pdf.png"
      disabled={!editor.project || exporting}
      loading={exporting}
      onClick={handleExportProjectToPDF}
    />
  );
}

function DeleteProjectOption({ editor }: { editor: ProjectEditorState }) {
  const navigate = useNavigate();
  const [deleteProject] = useDeleteProjectMutation();
  const [deleting, setDeleting] = useState(false);

  const handleDeleteProject = useCallback(async () => {
    if (editor.project) {
      try {
        setDeleting(true);
        await deleteProject(editor.project.id).unwrap();
      } finally {
        setDeleting(false);
      }
      navigate("/");
    }
  }, [editor.project?.id]);

  return (
    <ContextMenuOption
      text="Delete project"
      icon="trash.png"
      disabled={!editor.project || deleting}
      loading={deleting}
      onClick={handleDeleteProject}
    />
  );
}

function SaveProjectOption({ editor }: { editor: ProjectEditorState }) {
  const dispatch = useAppDispatch();
  const [saving, setSaving] = useState(false);
  const [patchProject] = usePatchProjectMutation();

  const handleSaveProject = useCallback(async () => {
    if (editor.project) {
      try {
        setSaving(true);
        const revision = await patchProject({
          id: editor.project.id,
          revision: editor.project.revision,
          patch: editor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(projectSaved(revision));
      } finally {
        setSaving(false);
      }
    }
  }, [editor]);

  return (
    <ContextMenuOption
      text="Save"
      icon="sync.png"
      disabled={!editor.project || saving}
      loading={saving}
      onClick={handleSaveProject}
    />
  );
}

function SaveProjectAndExitOption({ editor }: { editor: ProjectEditorState }) {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [patchProject] = usePatchProjectMutation();

  const handleSaveProject = useCallback(async () => {
    if (editor.project) {
      try {
        setSaving(true);
        const revision = await patchProject({
          id: editor.project.id,
          revision: editor.project.revision,
          patch: editor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(projectSaved(revision));
        navigate("/");
      } finally {
        setSaving(false);
      }
    }
  }, [editor]);

  return (
    <ContextMenuOption
      text="Save and exit"
      icon="signout.png"
      disabled={!editor.project || saving}
      loading={saving}
      onClick={handleSaveProject}
    />
  );
}

function CopyProjectUrlOption({ projectId }: { projectId: string }) {
  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(
      location.origin + `${Config.proxy.basePath}/editor/project/${projectId}`,
    );
  }, [projectId]);

  return (
    <ContextMenuOption text="Copy link" icon="copy.png" onClick={handleCopy} />
  );
}

function ShareProjectOption({ projectId }: { projectId: string }) {
  const [shareProject] = usePublishProjectMutation();
  const [sharing, setSharing] = useState(false);

  const handleShareProject = useCallback(async () => {
    try {
      setSharing(true);
      await shareProject(projectId).unwrap();
    } finally {
      setSharing(false);
    }
  }, [projectId]);

  return (
    <ContextMenuOption
      text="Share project"
      icon="share.png"
      disabled={sharing}
      loading={sharing}
      onClick={handleShareProject}
    />
  );
}

function HideProjectOption({ projectId }: { projectId: string }) {
  const [hideProject] = useUnpublishProjectMutation();
  const [hiding, setHiding] = useState(false);

  const handleHideProject = useCallback(async () => {
    try {
      setHiding(true);
      await hideProject(projectId).unwrap();
    } finally {
      setHiding(false);
    }
  }, [projectId]);

  return (
    <ContextMenuOption
      text="Hide project"
      icon="hide.png"
      disabled={hiding}
      loading={hiding}
      onClick={handleHideProject}
    />
  );
}

function ExitOption() {
  const navigate = useNavigate();

  const handleExitProject = useCallback(async () => {
    navigate("/");
  }, []);

  return (
    <ContextMenuOption
      text="Exit"
      icon="signout.png"
      onClick={handleExitProject}
    />
  );
}

export function MenuButton({
  projectId,
  projectOwned,
}: {
  projectId: string;
  projectOwned: boolean;
}) {
  const editor = useAppSelector(selectProjectEditor);
  const { data: project, isSuccess: projectLoaded } =
    useGetProjectByIdQuery(projectId);

  return (
    <ContextMenu
      content={
        <>
          {projectOwned && (
            <>
              <SaveProjectAndExitOption editor={editor} />
              <SaveProjectOption editor={editor} />
              <DeleteProjectOption editor={editor} />
              <ContextMenu
                content={
                  projectLoaded &&
                  (project.published ? (
                    <>
                      <HideProjectOption projectId={projectId} />
                      <CopyProjectUrlOption projectId={projectId} />
                    </>
                  ) : (
                    <>
                      <ShareProjectOption projectId={projectId} />
                    </>
                  ))
                }
                position="right"
              >
                <ContextMenuOption text="Share" icon="share.png" />
              </ContextMenu>
            </>
          )}
          {!projectOwned && <ExitOption />}
          <ExportProjectToPDFOption
            editor={editor}
            projectOwned={projectOwned}
          />
        </>
      }
    >
      <Button icon="menu.png" disabled={!editor.project} />
    </ContextMenu>
  );
}
