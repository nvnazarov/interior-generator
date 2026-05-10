import "./HomePage.scss";
import { ProjectsList } from "../slices/projects";
import {
  DeleteMyAccountButton,
  Profile,
  SignOutButton,
} from "../slices/account";

export function HomePage() {
  return (
    <div className="home-page">
      <div className="home-page__container">
        <div className="home-page__header">
          <DeleteMyAccountButton />
          <SignOutButton />
        </div>
        <Profile />
        <ProjectsList />
      </div>
    </div>
  );
}
