import { useCallback } from "react";
import { useFindAccountByIdQuery } from "../api/slice";
import { useAppSelector } from "../storeTypes";
import { Avatar } from "./Avatar";
import { selectMyAccount } from "./slice";
import { useNavigate } from "react-router";

export function SmartAvatar({ accountId }: { accountId: string }) {
  const navigate = useNavigate();
  const myAccount = useAppSelector(selectMyAccount);
  const { data: account, isSuccess } = useFindAccountByIdQuery(accountId);

  const handleClick = useCallback(() => {
    if (myAccount?.id === accountId) {
      navigate("/profile");
    }
  }, [myAccount?.id, accountId]);

  if (!isSuccess) {
    return <Avatar name="?" avatarUrl={null} />;
  }

  return (
    <Avatar
      onClick={handleClick}
      name={account.name}
      avatarUrl={account.image}
    />
  );
}
