import {
  forwardRef,
  type InputHTMLAttributes,
  type LabelHTMLAttributes,
} from "react";

import "./Toggle.scss";
import { Icon } from "../icon/Icon";

export type CustomAttributes = {
  text?: string;
  icon?: string;
};

export const Toggle = forwardRef<
  HTMLLabelElement,
  Omit<
    InputHTMLAttributes<HTMLInputElement>,
    "type" | "onPointerEnter" | "onPointerLeave"
  > &
    Pick<
      LabelHTMLAttributes<HTMLLabelElement>,
      "onPointerEnter" | "onPointerLeave"
    > &
    CustomAttributes
>(({ icon, text, onPointerEnter, onPointerLeave, ...props }, ref) => {
  return (
    <label
      ref={ref}
      className="toggle"
      onPointerEnter={onPointerEnter}
      onPointerLeave={onPointerLeave}
    >
      <input type="checkbox" className="toggle" {...props} />
      <span className="toggle__checkmark">
        <Icon src={icon} /> {text}
      </span>
    </label>
  );
});
