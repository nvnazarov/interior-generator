import { useParams } from "react-router";
import { Page } from "../shared/components";
import { PlanEditor } from "../slices/planEditor/PlanEditor";

export function PlanEditorPage() {
  const { projectId, planId } = useParams();

  if (!projectId) {
    throw new Error(
      "error: plan editor page: cannot get project id from params",
    );
  }
  if (!planId) {
    throw new Error("error: plan editor page: cannot get plan id from params");
  }

  return (
    <Page>
      <PlanEditor planId={planId} projectId={projectId} />
    </Page>
  );
}
