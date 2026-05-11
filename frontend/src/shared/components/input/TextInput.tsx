import { forwardRef, type InputHTMLAttributes } from "react";

import "./TextInput.scss";

type CustomAttributes = {
  maxLength?: number;
};

export const TextInput = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement> & CustomAttributes
>(({ maxLength, ...props }, ref) => {
  return <input {...props} className="text-input" ref={ref} />;
});
