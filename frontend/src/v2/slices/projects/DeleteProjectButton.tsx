import { useCallback, useState } from "react";
import { useDeleteProjectMutation } from "../api/slice";
import { Button } from "../../shared/components";

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
    <Button onClick={handleClick} disabled={isDeleting} icon="trash.png" />
  );
}
