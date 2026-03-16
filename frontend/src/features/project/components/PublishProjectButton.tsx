import { useState } from "react";
import { useAppDispatch } from "../../../app/hooks";
import { publishProject, unpublishProject } from "../slice";
import type { Project } from "../project";

export interface Props {
  project: Project;
}
export function PublishProjectButton({ project }: Props) {
  const dispatch = useAppDispatch();
  const [busy, setBusy] = useState(false);

  const handleClick = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();
    try {
      setBusy(true);
      if (project.published) {
        await dispatch(unpublishProject(project.id)).unwrap();
      } else {
        await dispatch(publishProject(project.id)).unwrap();
      }
    } catch (e) {
      // TODO
    } finally {
      setBusy(false);
    }
  };

  return (
    <button onClick={(e) => handleClick(e)} disabled={busy}>
      {project.published ? "Unpublish" : "Publish"}
    </button>
  );
}
