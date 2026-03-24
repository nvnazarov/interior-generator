import { NavLink } from "react-router";
import { Profile } from "../slices/account";
import { Center, Page } from "../shared/components";

export function ProfilePage() {
  return (
    <Page>
      <NavLink to="/profile">profile</NavLink>
      <NavLink to="/">home</NavLink>
      <Center>
        <Profile />
      </Center>
    </Page>
  );
}
