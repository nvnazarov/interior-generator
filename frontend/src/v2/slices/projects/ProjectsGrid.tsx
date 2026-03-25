import "./ProjectsGrid.scss";
import { useGetAllOwnedProjectsQuery } from "../api/slice";
import { DeleteProjectButton } from "./DeleteProjectButton";
import { ShareProjectButton } from "./ShareProjectButton";
import { ExportProjectToPdfButton } from "./ExportProjectToPdfButton";
import { CreateProjectButton } from "./CreateProjectButton";
import moment from "moment";
import type { Project } from "../api/entities";
import { useCallback, useState } from "react";

function Item({ project }: { project: Project }) {
  const [isMouseOver, setIsMouseOver] = useState(false);

  const handleMouseEnter = useCallback(() => {
    setIsMouseOver(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsMouseOver(false);
  }, []);

  return (
    <div
      className="projects__projects-grid__item"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div>
        <h1>{project.name || "Untitled Project"}</h1>
        <p>{project.description || "No description"}</p>
        <span>
          {moment(project.dtCreated).format("DD.MM.YYYY \\a\\t hh:mm")}
        </span>
      </div>
      <div style={{ opacity: isMouseOver ? 1 : 0 }}>
        <DeleteProjectButton projectId={project.id} />
        <ShareProjectButton projectId={project.id} />
        <ExportProjectToPdfButton projectId={project.id} />
      </div>
    </div>
  );
}

export function ProjectsGrid() {
  const { data, isLoading } = useGetAllOwnedProjectsQuery();
  if (isLoading) {
    return <div>Loading</div>;
  }
  if (!data) {
    return <div>No data</div>;
  }
  return (
    <div className="projects__projects-grid">
      <div className="projects__projects-grid__placeholder">
        <CreateProjectButton />
      </div>
      {data.map((project) => (
        <Item key={project.id} project={project} />
      ))}
    </div>
  );
}
