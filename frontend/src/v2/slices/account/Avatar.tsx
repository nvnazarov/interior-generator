import "./Avatar.scss";
import type { Account } from "./slice";

function getInitials(name: string): string {
  return name.slice(0, 2).toUpperCase();
}

export function Avatar({
  name,
  avatarUrl,
}: Pick<Partial<Account>, "name" | "avatarUrl">) {
  return (
    <div className="account__avatar">
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
