import "./Button.scss";
import type { MouseEventHandler } from "react";

export function Button({
  title,
  icon,
  disabled,
  onClick,
}: {
  title?: string;
  icon?: string;
  disabled?: boolean;
  onClick?: MouseEventHandler<HTMLButtonElement>;
}) {
  return (
    <button className="shared__button" onClick={onClick} disabled={disabled}>
      {icon && <img src={`/app/icons/${icon}`} />} {title}
    </button>
  );
}
