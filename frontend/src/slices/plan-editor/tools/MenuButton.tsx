import { useCallback, useState } from "react";
import { Button } from "../../../shared/components/button/Button";
import { useNavigate } from "react-router";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import {
  useDeletePlanMutation,
  useGetProjectByIdQuery,
  usePatchPlanMutation,
  usePublishProjectMutation,
  useUnpublishProjectMutation,
} from "../../api/slice";
import { planSaved, selectPlanEditor, type PlanEditorState } from "../slice";
import { Config } from "../../../shared/config";
import { UrlUtil } from "../../../shared/util";
import { ContextMenu } from "../../../shared/components/context-menu/ContextMenu";
import { ContextMenuOption } from "../../../shared/components/context-menu/ContextMenuOption";
import { notify } from "../../notifications/slice";

function ExportProjectToPDFOption({
  editor,
  projectOwned,
}: {
  editor: PlanEditorState;
  projectOwned: boolean;
}) {
  const dispatch = useAppDispatch();
  const [exporting, setExporting] = useState(false);
  const [patchPlan] = usePatchPlanMutation();

  const handleExportProjectToPDF = useCallback(async () => {
    if (!editor.plan) {
      return;
    }
    try {
      setExporting(true);
      if (projectOwned) {
        const revision = await patchPlan({
          id: editor.plan.id,
          revision: editor.plan.revision,
          patch: editor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(planSaved(revision));
      }
      const resp = await fetch(
        `${UrlUtil.noRightSlash(Config.gateway.baseUrl)}/api/projects/${editor.plan.projectId}/export/pdf`,
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
      a.download = `${editor.plan.projectId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      dispatch(
        notify({
          text: "Unable to export the project to PDF",
          severity: "error",
        }),
      );
    } finally {
      setExporting(false);
    }
  }, [editor]);

  return (
    <ContextMenuOption
      text="Export to PDF"
      icon="pdf.png"
      disabled={!editor.plan || exporting}
      loading={exporting}
      onClick={handleExportProjectToPDF}
    />
  );
}

function DeletePlanOption({ planId }: { planId: string }) {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [deletePlan] = useDeletePlanMutation();
  const [deleting, setDeleting] = useState(false);

  const handleDeletePlan = useCallback(async () => {
    try {
      setDeleting(true);
      await deletePlan(planId).unwrap();
      navigate("/");
    } catch {
      dispatch(
        notify({
          text: "Unable to delete the plan",
          severity: "error",
        }),
      );
    } finally {
      setDeleting(false);
    }
  }, [planId]);

  return (
    <ContextMenuOption
      text="Delete plan"
      icon="trash.png"
      disabled={deleting}
      loading={deleting}
      onClick={handleDeletePlan}
    />
  );
}

function SavePlanOption({ editor }: { editor: PlanEditorState }) {
  const dispatch = useAppDispatch();
  const [saving, setSaving] = useState(false);
  const [patchPlan] = usePatchPlanMutation();

  const handleSavePlan = useCallback(async () => {
    if (editor.plan) {
      try {
        setSaving(true);
        const revision = await patchPlan({
          id: editor.plan.id,
          revision: editor.plan.revision,
          patch: editor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(planSaved(revision));
      } catch {
        dispatch(
          notify({
            text: "Unable to save the plan",
            severity: "error",
          }),
        );
      } finally {
        setSaving(false);
      }
    }
  }, [editor]);

  return (
    <ContextMenuOption
      text="Save"
      icon="sync.png"
      disabled={!editor.plan || saving}
      loading={saving}
      onClick={handleSavePlan}
    />
  );
}

function SavePlanAndExitOption({ editor }: { editor: PlanEditorState }) {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [patchPlan] = usePatchPlanMutation();

  const handleSavePlan = useCallback(async () => {
    if (editor.plan) {
      try {
        setSaving(true);
        const revision = await patchPlan({
          id: editor.plan.id,
          revision: editor.plan.revision,
          patch: editor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(planSaved(revision));
        navigate("/");
      } catch {
        dispatch(
          notify({
            text: "Unable to save the plan",
            severity: "error",
          }),
        );
      } finally {
        setSaving(false);
      }
    }
  }, [editor]);

  return (
    <ContextMenuOption
      text="Save and exit"
      icon="signout.png"
      disabled={!editor.plan || saving}
      loading={saving}
      onClick={handleSavePlan}
    />
  );
}

function CopyPlanUrlOption({
  projectId,
  planId,
}: {
  projectId: string;
  planId: string;
}) {
  const dispatch = useAppDispatch();

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(
      location.origin +
        `${Config.proxy.basePath}/editor/project/${projectId}/plan/${planId}`,
    );
    dispatch(
      notify({
        text: "Copied plan URL to clipboard",
        severity: "info",
      }),
    );
  }, [projectId]);

  return (
    <ContextMenuOption text="Copy link" icon="copy.png" onClick={handleCopy} />
  );
}

function ShareProjectOption({ projectId }: { projectId: string }) {
  const dispatch = useAppDispatch();
  const [shareProject] = usePublishProjectMutation();
  const [sharing, setSharing] = useState(false);

  const handleShareProject = useCallback(async () => {
    try {
      setSharing(true);
      await shareProject(projectId).unwrap();
    } catch {
      dispatch(
        notify({
          text: "Unable to share the project",
          severity: "error",
        }),
      );
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
  const dispatch = useAppDispatch();
  const [hideProject] = useUnpublishProjectMutation();
  const [hiding, setHiding] = useState(false);

  const handleHideProject = useCallback(async () => {
    try {
      setHiding(true);
      await hideProject(projectId).unwrap();
    } catch {
      dispatch(
        notify({
          text: "Unable to hide the project",
          severity: "error",
        }),
      );
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
  planId,
  projectOwned,
}: {
  projectId: string;
  planId: string;
  projectOwned: boolean;
}) {
  const editor = useAppSelector(selectPlanEditor);
  const { data: project, isSuccess: projectLoaded } =
    useGetProjectByIdQuery(projectId);

  return (
    <ContextMenu
      content={
        <>
          {projectOwned && (
            <>
              <SavePlanAndExitOption editor={editor} />
              <SavePlanOption editor={editor} />
              <DeletePlanOption planId={planId} />
              <ContextMenu
                content={
                  projectLoaded &&
                  (project.published ? (
                    <>
                      <HideProjectOption projectId={projectId} />
                      <CopyPlanUrlOption
                        projectId={projectId}
                        planId={planId}
                      />
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
      <Button icon="menu.png" disabled={!editor.plan} />
    </ContextMenu>
  );
}
