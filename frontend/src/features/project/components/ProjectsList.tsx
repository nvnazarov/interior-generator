import { fetchAllOwnedProjects, selectAllProjects } from "../slice";
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { ProjectInList } from "./ProjectInList";
import { useEffect } from "react";

export function ProjectsList() {
  const dispatch = useAppDispatch();
  const projects = useAppSelector(selectAllProjects);

  useEffect(() => {
    dispatch(fetchAllOwnedProjects());
  }, [dispatch]);

  return (
    <div>
      {projects.map((project) => (
        <ProjectInList key={project.id} project={project} />
      ))}
    </div>
  );
}
