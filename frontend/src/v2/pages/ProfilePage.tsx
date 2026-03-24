import { NavLink } from "react-router";
import { Profile, SignOutButton } from "../slices/account";
import { Center, Page } from "../shared/components";

export function ProfilePage() {
  return (
    <Page>
      <div>
        <SignOutButton />
        <NavLink to="/profile">profile</NavLink>
        <NavLink to="/">home</NavLink>
      </div>
      <Center>
        <Profile />
      </Center>
    </Page>
  );
}
