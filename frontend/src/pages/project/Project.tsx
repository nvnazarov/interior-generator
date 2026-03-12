import { Link, useParams } from "react-router";
import { ProjectEditor } from "../../features/project/ProjectEditor";

export function Project() {
  const { id } = useParams();

  if (!id) {
    throw new Error("bug");
  }

  return (
    <div>
      <div>
        <Link to="/projects">All projects</Link>
      </div>
      <ProjectEditor id={id} />
    </div>
  );
}
