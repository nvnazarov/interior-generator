import "./Page.scss";
import type { ReactNode } from "react";

export function Page({ children }: { children: ReactNode }) {
  return <div className="shared__page">{children}</div>;
}
