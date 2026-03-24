import { NavLink } from "react-router";
import { ProjectsList } from "../slices/projects/ProjectsList";
import { SignOutButton } from "../slices/account";

export function HomePage() {
  return (
    <div>
      <div>
        <SignOutButton />
        <NavLink to="/profile">profile</NavLink>
        <NavLink to="/">home</NavLink>
      </div>
      <ProjectsList />
    </div>
  );
}
