import { NavLink } from "react-router";
import { ProjectsList, CreateProjectButton } from "../slices/projects";
import { SignOutButton } from "../slices/account";

export function HomePage() {
  return (
    <div>
      <div>
        <SignOutButton />
        <NavLink to="/profile">profile</NavLink>
        <NavLink to="/">home</NavLink>
      </div>
      <CreateProjectButton />
      <ProjectsList />
    </div>
  );
}
