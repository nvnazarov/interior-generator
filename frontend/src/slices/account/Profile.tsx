import "./Profile.scss";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { accountUpdated, selectMyAccount } from "./slice";
import moment from "moment";
import { DeleteMyAccountButton } from "./DeleteMyAccountButton";
import { useCallback, useEffect, useState, type ChangeEvent } from "react";
import { authClient } from "../../shared/betterAuth";
import { Avatar } from "./Avatar";
import { Client } from "../../shared/client";
import { useTranslation } from "react-i18next";
import { Button } from "../../shared/components";
import i18next from "i18next";

const MAX_AVATAR_FILE_SIZE_BYTES = 512 * 1024;

export function Profile() {
  const dispatch = useAppDispatch();
  const { t } = useTranslation();
  const [mode, setMode] = useState<"view" | "edit">("view");
  const account = useAppSelector(selectMyAccount);
  const dtCreated = moment(account?.dtCreated);
  const [editedName, setEditedName] = useState(account?.name || "");
  const [isSaving, setIsSaving] = useState(false);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(null);

  const isDirty = editedName !== account?.name || avatarFile;

  const handleSave = useCallback(async () => {
    if (isSaving) {
      return;
    }
    const userUpdate = {
      name: editedName,
    } as any;
    if (avatarFile) {
      const avatarId = await Client.createAvatar(avatarFile);
      userUpdate["image"] = `/assets/avatars/${avatarId}`;
    }
    await authClient
      .updateUser(userUpdate)
      .then((data) => {
        if (data.error) {
          // TODO
        } else {
          dispatch(
            accountUpdated({ name: editedName, avatarUrl: userUpdate.image }),
          );
          setMode("view");
        }
      })
      .finally(() => setIsSaving(false));
  }, [editedName, isSaving, avatarFile]);

  const handleSwitchToEditMode = useCallback(() => {
    setMode("edit");
    setEditedName(account?.name || editedName);
    if (avatarPreviewUrl) {
      URL.revokeObjectURL(avatarPreviewUrl);
    }
    setAvatarPreviewUrl(null);
    setAvatarFile(null);
  }, [account]);

  const handleNameChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setEditedName(e.target.value);
  }, []);

  const handleCancel = useCallback(() => {
    setMode("view");
    setEditedName(account?.name || editedName);
    if (avatarPreviewUrl) {
      URL.revokeObjectURL(avatarPreviewUrl);
    }
    setAvatarPreviewUrl(null);
    setAvatarFile(null);
  }, [account]);

  const handleAvatarFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      if (!e.target.files) {
        return;
      }
      const file = e.target.files[0];
      if (!file) {
        return;
      }
      if (file.size > MAX_AVATAR_FILE_SIZE_BYTES) {
        return;
      }
      setAvatarFile(file);
      const url = URL.createObjectURL(file);
      if (avatarPreviewUrl) {
        URL.revokeObjectURL(avatarPreviewUrl);
      }
      setAvatarPreviewUrl(url);
    },
    [MAX_AVATAR_FILE_SIZE_BYTES],
  );

  useEffect(() => {
    return () => {
      if (avatarPreviewUrl) {
        URL.revokeObjectURL(avatarPreviewUrl);
      }
    };
  }, [avatarPreviewUrl]);

  return (
    <div className="account__profile">
      <div className="account__profile__title">
        USER LICENSE <hr />
      </div>
      <div className="account__profile__data">
        {mode === "view" ? (
          <Avatar name={account?.name} avatarUrl={account?.avatarUrl} />
        ) : (
          <div>
            <input
              id="avatar-file-input"
              accept="image/png, image/jpeg"
              type="file"
              style={{ display: "none" }}
              onChange={handleAvatarFileChange}
            />
            <label htmlFor="avatar-file-input">
              <Avatar
                name={account?.name}
                avatarUrl={avatarPreviewUrl || account?.avatarUrl}
              />
            </label>
          </div>
        )}
        <table>
          <tbody>
            <tr>
              <td className="account__profile__attr__name">
                {t("Account.Profile.Name.Title")}
              </td>
              <td className="account__profile__attr__value">
                {mode === "edit" ? (
                  <input
                    placeholder="your name"
                    value={editedName}
                    onChange={handleNameChange}
                  />
                ) : (
                  account?.name
                )}
              </td>
            </tr>
            <tr>
              <td className="account__profile__attr__name">
                {t("Account.Profile.Lang.Title")}
              </td>
              <td className="account__profile__attr__value">
                {i18next.language}
              </td>
            </tr>
            <tr>
              <td className="account__profile__attr__name">
                {t("Account.Profile.Date.Title", "Date")}
              </td>
              <td className="account__profile__attr__value">
                {dtCreated.format(
                  t("Account.Profile.Date.Format", "DD.MM.YYYY"),
                )}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="account__profile__actions">
        {mode === "view" ? (
          <>
            <DeleteMyAccountButton />
            <button onClick={handleSwitchToEditMode}>Edit</button>
          </>
        ) : (
          <>
            <Button
              onClick={handleCancel}
              title={t("Account.Profile.Edit.CancelButton.Title", "Cancel")}
            />
            <Button
              onClick={handleSave}
              disabled={isSaving || !isDirty}
              title={t("Account.Profile.Edit.SaveButton.Title", "Save")}
            />
          </>
        )}
      </div>
    </div>
  );
}
