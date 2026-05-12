import { useAppSelector } from "../../../storeTypes";
import { Avatar } from "./Avatar";
import { selectMyAccount } from "../../slice";

export function MyAvatar() {
  const account = useAppSelector(selectMyAccount);
  return <Avatar name={account?.name} avatarUrl={account?.avatarUrl} />;
}
