import type React from "react";
import { useCallback, useState } from "react";
import { useNavigate } from "react-router";

import { authClient } from "../../../../shared/betterAuth";
import { useAppDispatch } from "../../../storeTypes";
import { accountDeleted } from "../../slice";
import { notify } from "../../../notifications/slice";
import { Button } from "../../../../shared/components/button/Button";
import { useTranslation } from "react-i18next";

export function DeleteMyAccountButton() {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  const handleClick = useCallback((_: React.MouseEvent<HTMLButtonElement>) => {
    if (deleting) {
      return;
    }
    setDeleting(true);
    authClient
      .deleteUser()
      .then((res) => {
        if (res.error) {
          throw new Error(res.error.message);
        } else {
          dispatch(accountDeleted());
          navigate("/sign-in", { replace: true });
        }
      })
      .catch(() => {
        dispatch(
          notify({ text: "Unable to delete the account", severity: "error" }),
        );
      })
      .finally(() => setDeleting(false));
  }, []);

  return (
    <Button
      onClick={handleClick}
      loading={deleting}
      danger
      text={t("Account.DeleteAccount", "Delete account")}
    />
  );
}
