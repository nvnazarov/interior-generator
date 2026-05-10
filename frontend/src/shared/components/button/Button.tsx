import { forwardRef, type ButtonHTMLAttributes } from "react";

import "./Button.scss";

export type CustomAttributes = {
  text?: string;
  icon?: string;
  danger?: boolean;
  primary?: boolean;
  loading?: boolean;
};

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & CustomAttributes
>(({ text, icon, primary, danger, loading, ...props }, ref) => {
  const class_ = primary
    ? "button--primary"
    : danger
      ? "button--danger"
      : "button";
  return (
    <button className={class_} {...props} ref={ref}>
      {loading ? <></> : icon && <></>} {text}
    </button>
  );
});
