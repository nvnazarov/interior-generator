import { useState } from "react";
import { useNavigate } from "react-router";
import { useAppDispatch } from "../../app/hooks";
import {
  createProject,
  MAX_PROJECTS_COUNT,
  selectTotalProjects,
} from "./projectSlice";
import { useSelector } from "react-redux";

export function CreateProjectButton() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const totalProjects = useSelector(selectTotalProjects);
  const [busy, setBusy] = useState(false);

  const handleClick = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();
    try {
      setBusy(true);
      const project = await dispatch(createProject()).unwrap();
      navigate(`/projects/${project.id}`);
    } catch (e) {
      // TODO
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      onClick={(e) => handleClick(e)}
      title={
        (totalProjects >= MAX_PROJECTS_COUNT &&
          `You can only own ${MAX_PROJECTS_COUNT} projects`) ||
        undefined
      }
      disabled={busy || totalProjects >= MAX_PROJECTS_COUNT}
    >
      Create
    </button>
  );
}
