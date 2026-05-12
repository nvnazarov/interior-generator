import { Navigate, useParams } from "react-router";

import "./ProjectEditorPage.scss";
import { ProjectEditor } from "../../slices/project-editor/ProjectEditor";

export function ProjectEditorPage() {
  const { projectId } = useParams();

  if (!projectId) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="project-editor-page">
      <ProjectEditor projectId={projectId} />
    </div>
  );
}
