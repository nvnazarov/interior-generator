import { useParams } from "react-router";
import { Page } from "../shared/components";
import { ProjectEditor } from "../slices/projectEditor/ProjectEditor";

export function PlanEditorPage() {
  const { projectId, planId } = useParams();

  if (!projectId) {
    throw new Error(
      "error: plan editor page: cannot get project id from params",
    );
  }
  if (!planId) {
    throw new Error(
      "error: plan editor page: cannot get plan id from params",
    );
  }

  return (
    <Page>
      <ProjectEditor projectId={projectId} />
    </Page>
  );
}
