import { useCallback, useState } from "react";
import { useCreateProjectMutation } from "../api/slice";
import { useNavigate } from "react-router";
import { Button } from "../../shared/components";

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
    <Button
      onClick={handleClick}
      disabled={isCreating}
      title="Create project"
    />
  );
}
