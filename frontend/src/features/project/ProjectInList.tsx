import type { Project } from "./projectSlice";
import "./ProjectInList.scss";
import { DeleteProjectButton } from "./DeleteProjectButton";
import { Link } from "react-router";
import { PublishProjectButton } from "./PublishProjectButton";
import moment from "moment";
import { ExportProjectPDFButton } from "./ExportProjectPDFButton";

export interface Props {
  project: Project;
}

export function ProjectInList({ project }: Props) {
  const fmt = (date: string) => moment(date).fromNow();

  return (
    <div className="project-in-list">
      <Link to={`/projects/${project.id}`}>{project.name || "Untitled"}</Link>{" "}
      {fmt(project.updated_at)} {project.published}
      <DeleteProjectButton id={project.id} />
      <PublishProjectButton project={project} />
      <ExportProjectPDFButton id={project.id} />
    </div>
  );
}
