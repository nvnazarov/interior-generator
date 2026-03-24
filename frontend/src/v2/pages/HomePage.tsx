import { NavLink } from "react-router";
import { ProjectsList } from "../slices/projects/ProjectsList";

export function HomePage() {
  return (
    <div>
      <NavLink to="/profile">profile</NavLink>
      <NavLink to="/">home</NavLink>
      <ProjectsList />
    </div>
  );
}
