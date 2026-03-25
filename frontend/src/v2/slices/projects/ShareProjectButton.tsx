import { useCallback, useState } from "react";
import {
  useGetAllOwnedProjectsQuery,
  usePublishProjectMutation,
  useUnpublishProjectMutation,
} from "../api/slice";

export function ShareProjectButton({ projectId }: { projectId: string }) {
  const { project } = useGetAllOwnedProjectsQuery(undefined, {
    selectFromResult: ({ data }) => ({
      project: data?.find((project) => project.id === projectId),
    }),
  });
  const [publishProject] = usePublishProjectMutation();
  const [unpublishProject] = useUnpublishProjectMutation();
  const [isBusy, setIsBusy] = useState(false);

  const handleClick = useCallback(async () => {
    try {
      setIsBusy(true);
      if (!project) {
        return;
      }
      if (project.published) {
        await unpublishProject(projectId).unwrap();
      } else {
        await publishProject(projectId).unwrap();
      }
    } catch {
      // TODO
    } finally {
      setIsBusy(false);
    }
  }, [project]);

  return (
    <button onClick={handleClick} disabled={isBusy}>
      {project?.published ? "Unpublish" : "Publish"}
    </button>
  );
}
