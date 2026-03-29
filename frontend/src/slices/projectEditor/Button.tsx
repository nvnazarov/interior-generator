import "./Button.scss";
import type { MouseEventHandler } from "react";

export function Button({
  title,
  icon,
  loading,
  active,
  disabled,
  onClick,
}: {
  title?: string;
  icon?: string;
  loading?: boolean;
  active?: boolean;
  disabled?: boolean;
  onClick?: MouseEventHandler<HTMLButtonElement>;
}) {
  const className = disabled
    ? "project-editor__button__disabled"
    : active
      ? "project-editor__button__active"
      : "project-editor__button";

  return (
    <button
      className={className}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {icon && (
        <img
          className="project-editor__button__icon"
          src={`/app/icons/${icon}`}
        />
      )}
      {title}
    </button>
  );
}
