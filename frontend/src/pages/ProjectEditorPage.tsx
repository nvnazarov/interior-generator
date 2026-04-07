import { useParams } from "react-router";
import { Page } from "../shared/components";
import { ProjectEditor } from "../slices/projectEditor/ProjectEditor";

export function ProjectEditorPage() {
  const { projectId } = useParams();

  if (!projectId) {
    throw new Error(
      "error: project editor page: cannot get project id from params",
    );
  }

  return (
    <Page>
      <ProjectEditor projectId={projectId} />
    </Page>
  );
}
