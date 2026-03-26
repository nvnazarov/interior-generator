import "./HomePage.scss";
import { NavLink } from "react-router";
import { ProjectsGrid } from "../slices/projects";
import { SignOutButton } from "../slices/account";
import { Center, Page } from "../shared/components";
import { ChangeLanguageButton } from "../slices/other";
import { MyAvatar } from "../slices/account/MyAvatar";

export function HomePage() {
  return (
    <Page>
      <div className="pages__home__header">
        <ChangeLanguageButton />
        <SignOutButton />
        <NavLink to="/profile">
          <MyAvatar />
        </NavLink>
      </div>
      <Center>
        <ProjectsGrid />
      </Center>
    </Page>
  );
}
