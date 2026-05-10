import { useCallback, useState } from "react";
import { useCreateProjectMutation } from "../api/slice";
import { useNavigate } from "react-router";
import { Button } from "../../shared/components/button/Button";

export function CreateProjectButton() {
  const navigate = useNavigate();
  const [createProject] = useCreateProjectMutation();
  const [processing, setProcessing] = useState(false);

  const handleClick = useCallback(async () => {
    try {
      setProcessing(true);
      const project = await createProject().unwrap();
      navigate(`/editor/project/${project.id}`);
    } catch {
      // TODO
    } finally {
      setProcessing(false);
    }
  }, []);

  return (
    <Button
      onClick={handleClick}
      text="Create project"
      disabled={processing}
      primary
    />
  );
}
