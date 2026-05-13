import moment from "moment";
import { useCallback, useEffect, useState, type ChangeEvent } from "react";

import "./Profile.scss";
import { useAppDispatch, useAppSelector } from "../../../storeTypes";
import { accountUpdated, selectMyAccount } from "../../slice";
import { authClient } from "../../../../shared/betterAuth";
import { Avatar } from "../avatar/Avatar";
import { Client } from "../../../../shared/client";
import { Button } from "../../../../shared/components/button/Button";
import { notify } from "../../../notifications/slice";
import { MAX_AVATAR_FILE_SIZE_BYTES } from "../../lib";
import { TextInput } from "../../../../shared/components/input/TextInput";

export function Profile() {
  const dispatch = useAppDispatch();
  const [mode, setMode] = useState<"view" | "edit">("view");
  const account = useAppSelector(selectMyAccount);
  const dtCreated = moment(account?.dtCreated);
  const [editedName, setEditedName] = useState(account?.name || "");
  const [isSaving, setIsSaving] = useState(false);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(null);

  const isDirty = editedName !== account?.name || Boolean(avatarFile);

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
          dispatch(notify({ text: data.error.message, severity: "error" }));
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
  }, [account, avatarPreviewUrl]);

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
  }, [account, avatarPreviewUrl]);

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
        dispatch(notify({ text: "Max file size is 512KB", severity: "error" }));
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
    <div className="profile">
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
              interactive
              name={account?.name}
              avatarUrl={avatarPreviewUrl || account?.avatarUrl}
            />
          </label>
        </div>
      )}
      {mode === "edit" ? (
        <TextInput
          placeholder="Name"
          value={editedName}
          onChange={handleNameChange}
        />
      ) : (
        <p>{account?.name}</p>
      )}
      <div className="profile__static-data">
        <p className="profile__email">{account?.email}</p>
        <p className="profile__register-date">
          Registered {dtCreated.format("DD.MM.YYYY")}
        </p>
      </div>
      <div className="profile__actions">
        {mode === "view" ? (
          <>
            <Button onClick={handleSwitchToEditMode} text="Edit" />
          </>
        ) : (
          <>
            <Button onClick={handleCancel} text="Cancel" />
            <Button
              onClick={handleSave}
              disabled={!isDirty}
              loading={isSaving && isDirty}
              primary
              text="Save"
            />
          </>
        )}
      </div>
    </div>
  );
}
