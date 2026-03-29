import "./ProfilePage.scss";
import { NavLink } from "react-router";
import { Profile, SignOutButton } from "../slices/account";
import { Center, Page } from "../shared/components";

export function ProfilePage() {
  return (
    <Page>
      <div className="pages__profile__header">
        <SignOutButton />
        <NavLink to="/">home</NavLink>
      </div>
      <Center>
        <Profile />
      </Center>
    </Page>
  );
}
