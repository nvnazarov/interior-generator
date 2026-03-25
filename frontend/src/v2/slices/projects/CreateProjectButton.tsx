import { useCallback, useState } from "react";
import { useCreateProjectMutation } from "../api/slice";
import { useNavigate } from "react-router";

export function CreateProjectButton() {
  const navigate = useNavigate();
  const [createProject] = useCreateProjectMutation();
  const [isCreating, setIsCreating] = useState(false);

  const handleClick = useCallback(async () => {
    try {
      setIsCreating(true);
      const project = await createProject().unwrap();
      navigate(`/editor/${project.id}`);
    } catch {
      // TODO
    } finally {
      setIsCreating(false);
    }
  }, []);

  return (
    <button onClick={handleClick} disabled={isCreating}>
      Create Project
    </button>
  );
}
