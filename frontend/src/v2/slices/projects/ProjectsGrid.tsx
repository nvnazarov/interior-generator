import "./ProjectsGrid.scss";
import { useGetAllOwnedProjectsQuery } from "../api/slice";
import { DeleteProjectButton } from "./DeleteProjectButton";
import { ShareProjectButton } from "./ShareProjectButton";
import { ExportProjectToPdfButton } from "./ExportProjectToPdfButton";
import { CreateProjectButton } from "./CreateProjectButton";
import moment from "moment";
import type { Project } from "../api/entities";
import { useCallback, useState } from "react";
import { useNavigate } from "react-router";
import { useTranslation } from "react-i18next";

function Item({ project }: { project: Project }) {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [isMouseOver, setIsMouseOver] = useState(false);

  const handleMouseEnter = useCallback(() => {
    setIsMouseOver(true);
  }, []);

  const handleMouseOver = useCallback(() => {
    setIsMouseOver(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsMouseOver(false);
  }, []);

  const handleClick = useCallback(() => {
    navigate(`/editor/project/${project.id}`);
  }, [project.id]);

  return (
    <div
      className="projects__projects-grid__item"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onMouseOver={handleMouseOver}
      onClick={handleClick}
    >
      <div>
        <h1>
          {project.name ||
            t("Projects.ProjectsGrid.Item.Name.Default", "Untitled Project")}
        </h1>
        <p>
          {project.description ||
            t(
              "Projects.ProjectsGrid.Item.Description.Default",
              "No description",
            )}
        </p>
        <span>
          {moment(project.dtCreated).format(
            t(
              "Projects.ProjectsGrid.Item.Date.Format",
              "DD.MM.YYYY \\a\\t hh:mm",
            ),
          )}
        </span>
      </div>
      <div
        style={{ opacity: isMouseOver ? 1 : 0 }}
        onClick={(e) => e.stopPropagation()}
      >
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
