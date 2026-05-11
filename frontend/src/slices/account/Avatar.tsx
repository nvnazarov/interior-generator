import type { HTMLAttributes } from "react";

import "./Avatar.scss";
import type { Account } from "./slice";
import { initials } from "./lib";

type AvatarAttributes = Pick<Partial<Account>, "name" | "avatarUrl"> & {
  interactive?: boolean;
  small?: boolean;
} & HTMLAttributes<HTMLDivElement>;

export function Avatar({
  name,
  interactive,
  small,
  avatarUrl,
  ...props
}: AvatarAttributes) {
  name = name ? name : "Anonymous";
  const classes_ =
    "avatar" +
    (interactive ? " avatar--interactive" : "") +
    (small ? " avatar--small" : "");
  return (
    <div className={classes_} {...props} title={name}>
      {avatarUrl ? <img src={avatarUrl} /> : initials(name)}
    </div>
  );
}
