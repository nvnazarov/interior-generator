import { useCallback } from "react";
import { useFindAccountByIdQuery } from "../api/slice";
import { useAppSelector } from "../storeTypes";
import { Avatar } from "./Avatar";
import { selectMyAccount } from "./slice";
import { useNavigate } from "react-router";

type AccountAvatarAttributes = {
  accountId: string;
  interactive?: boolean;
  small?: boolean;
};

export function AccountAvatar({
  accountId,
  interactive,
  small,
}: AccountAvatarAttributes) {
  const navigate = useNavigate();
  const myAccount = useAppSelector(selectMyAccount);
  const { data: account, isSuccess } = useFindAccountByIdQuery(accountId);

  const handleClick = useCallback(() => {
    if (myAccount?.id === accountId) {
      navigate("/profile");
    }
  }, [myAccount?.id, accountId]);

  if (!isSuccess) {
    return <Avatar interactive={interactive} small={small} />;
  }

  return (
    <Avatar
      onClick={handleClick}
      name={account.name}
      avatarUrl={account.image}
      interactive={interactive}
      small={small}
    />
  );
}
