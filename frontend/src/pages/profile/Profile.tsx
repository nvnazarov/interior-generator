import { Link } from "react-router";
import { LogoutButton, ProfileForm } from "../../features/account";
import "./Profile.scss";

export function Profile() {
  return (
    <div className="page-profile">
      <p>
        <Link to="/projects">See your projects</Link>
      </p>
      <ProfileForm />
      <LogoutButton />
    </div>
  );
}
