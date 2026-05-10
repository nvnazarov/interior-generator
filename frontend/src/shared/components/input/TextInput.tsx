import { forwardRef, type InputHTMLAttributes } from "react";

import "./TextInput.scss";

export const TextInput = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement>
>((props, ref) => {
  return <input {...props} className="text-input" ref={ref} />;
});
