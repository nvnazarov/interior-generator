import type React from "react";
import { authClient } from "../../shared/betterAuth";
import { useCallback, useState } from "react";
import { useNavigate } from "react-router";
import { useAppDispatch } from "../storeTypes";
import { accountDeleted } from "./slice";

export function DeleteMyAccountButton() {
  const dispatch = useAppDispatch();
  const [disabled, setDisabled] = useState(false);
  const navigate = useNavigate();

  const handleClick = useCallback((_: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled) {
      return;
    }
    setDisabled(true);
    authClient
      .deleteUser()
      .then((res) => {
        if (res.error) {
          // TODO
        } else {
          dispatch(accountDeleted());
          navigate("/sign-in", { replace: true });
        }
      })
      .finally(() => setDisabled(false));
  }, []);

  return (
    <button onClick={handleClick} disabled={disabled}>
      Delete
    </button>
  );
}
