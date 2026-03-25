import { useCallback, useState } from "react";
import { useDeleteProjectMutation } from "../api/slice";

export function DeleteProjectButton({ projectId }: { projectId: string }) {
  const [deleteProject] = useDeleteProjectMutation();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleClick = useCallback(async () => {
    try {
      setIsDeleting(true);
      await deleteProject(projectId).unwrap();
    } catch {
      // TODO
    } finally {
      setIsDeleting(false);
    }
  }, [projectId]);

  return (
    <button onClick={handleClick} disabled={isDeleting}>
      Delete Project
    </button>
  );
}
