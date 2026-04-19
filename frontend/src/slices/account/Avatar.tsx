import type React from "react";
import "./Avatar.scss";
import type { Account } from "./slice";

function getInitials(name: string): string {
  return name.slice(0, 2).toUpperCase();
}

export function Avatar({
  name,
  avatarUrl,
  onClick,
}: Pick<Partial<Account>, "name" | "avatarUrl"> & {
  onClick?: React.MouseEventHandler<HTMLDivElement>;
}) {
  return (
    <div className="account__avatar" onClick={onClick} title={name}>
      {avatarUrl ? (
        <img className="account__avatar__img" src={avatarUrl || undefined} />
      ) : name ? (
        <>{getInitials(name)}</>
      ) : (
        <>?</>
      )}
    </div>
  );
}
