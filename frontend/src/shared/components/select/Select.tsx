import { forwardRef, type SelectHTMLAttributes } from "react";

import "./Select.scss";

export const Select = forwardRef<
  HTMLSelectElement,
  SelectHTMLAttributes<HTMLSelectElement>
>(({ children, value, ...props }, ref) => {
  return (
    <select className="select" {...props} ref={ref}>
      {children}
    </select>
  );
});
