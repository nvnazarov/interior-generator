import { NavLink } from "react-router";
import { ProjectsGrid } from "../slices/projects";
import { SignOutButton } from "../slices/account";
import { Center, Page } from "../shared/components";

export function HomePage() {
  return (
    <Page>
      <div>
        <SignOutButton />
        <NavLink to="/profile">profile</NavLink>
        <NavLink to="/">home</NavLink>
      </div>
      <Center>
        <ProjectsGrid />
      </Center>
    </Page>
  );
}
