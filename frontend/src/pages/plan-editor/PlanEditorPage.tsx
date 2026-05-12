import { Navigate, useParams } from "react-router";

import "./PlanEditorPage.scss";
import { PlanEditor } from "../../slices/plan-editor/PlanEditor";

export function PlanEditorPage() {
  const { projectId, planId } = useParams();

  if (!projectId || !planId) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="plan-editor-page">
      <PlanEditor planId={planId} projectId={projectId} />
    </div>
  );
}
