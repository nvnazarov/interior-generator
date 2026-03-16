import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import "./ProjectInfo.scss";
import { optimisticPatchProject, selectProjectById } from "../slice";
import { useEffect, useState, type ChangeEvent } from "react";

export interface Props {
  projectId: string;
}

export function ProjectInfo({ projectId }: Props) {
  const dispatch = useAppDispatch();
  const project = useAppSelector(selectProjectById(projectId));
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    if (project) {
      setName(project.name);
      setDescription(project.description);
    }
  }, [project]);

  function handleNameChange(e: ChangeEvent<HTMLInputElement>) {
    setName(e.target.value);
  }

  function handleDescriptionChange(e: ChangeEvent<HTMLInputElement>) {
    setDescription(e.target.value);
  }

  function handleInfoClick() {
    setIsDialogOpen(!isDialogOpen);
  }

  function handleCancelClick() {
    setIsDialogOpen(false);
  }

  function handleSaveClick() {
    dispatch(
      optimisticPatchProject({ id: projectId, patch: { name, description } }),
    );
    setIsDialogOpen(false);
  }

  return (
    <div className="project__info" onClick={handleInfoClick}>
      {project?.name || "Untitled Project"}
      <div
        style={{ display: isDialogOpen ? "block" : "none" }}
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault();
        }}
      >
        <form className="project__info__dialog">
          <div>
            <input
              type="text"
              value={name}
              onChange={handleNameChange}
              placeholder="Project Name"
            />
          </div>
          <div>
            <input
              type="text"
              value={description}
              onChange={handleDescriptionChange}
              placeholder="Project Description"
            />
          </div>
          <div className="project__info__dialog__actions">
            <button onClick={handleCancelClick}>Cancel</button>
            <button onClick={handleSaveClick}>Save</button>
          </div>
        </form>
      </div>
    </div>
  );
}
