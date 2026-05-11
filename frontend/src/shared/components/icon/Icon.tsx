import { forwardRef, type ImgHTMLAttributes } from "react";

import "./Icon.scss";

export const Icon = forwardRef<
  HTMLImageElement,
  ImgHTMLAttributes<HTMLImageElement>
>(({ src, ...props }, ref) => {
  return (
    <img className="icon" ref={ref} src={`/app/icons/${src}`} {...props} />
  );
});
