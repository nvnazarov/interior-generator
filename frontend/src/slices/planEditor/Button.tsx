import "./Button.scss";
import type { ButtonHTMLAttributes } from "react";

type ButtonAttributes = {
  title?: string;
  icon?: string;
  loading?: boolean;
  active?: boolean;
} & ButtonHTMLAttributes<HTMLButtonElement>;

export function Button(attributes: ButtonAttributes) {
  const className = attributes.disabled
    ? "plan-editor__button__disabled"
    : attributes.active
      ? "plan-editor__button__active"
      : "plan-editor__button";

  const buttonAttibutes = Object.assign(
    {},
    ...(Object.keys(attributes) as (keyof ButtonAttributes)[])
      .filter((a) => !["title", "icon", "loading", "active"].includes(a))
      .map((key) => ({ [key]: attributes[key] })),
  );

  return (
    <button className={className} {...buttonAttibutes}>
      {attributes.icon && (
        <img
          className="plan-editor__button__icon"
          src={`/app/icons/${attributes.icon}`}
        />
      )}
      {attributes.title}
    </button>
  );
}
