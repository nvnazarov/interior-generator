import { forwardRef, type ButtonHTMLAttributes } from "react";

import "./ContextMenuOption.scss";
import { Icon } from "../icon/Icon";

export type CustomAttributes = {
  text?: string;
  icon?: string;
  loading?: boolean;
};

export const ContextMenuOption = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & CustomAttributes
>(({ text, icon, loading, ...props }, ref) => {
  return (
    <button className="context-menu-option" ref={ref} {...props}>
      {loading ? (
        <span className="context-menu-option__spinner" />
      ) : (
        icon && <Icon src={icon} />
      )}{" "}
      {text}
    </button>
  );
});
