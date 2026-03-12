import "./Projects.scss";

import { ProjectsList } from "../../features/project";
import { CreateProjectButton } from "../../features/project/CreateProjectButton";
import { Link } from "react-router";

export function Projects() {
  return (
    <div className="projects">
      <p>
        <Link to="/profile">See your profile</Link>
      </p>
      <CreateProjectButton />
      <ProjectsList />
    </div>
  );
}
