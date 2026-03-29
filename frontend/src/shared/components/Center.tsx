import "./Center.scss";
import type { ReactNode } from "react";

export function Center({ children }: { children: ReactNode }) {
  return <div className="shared__center">{children}</div>;
}
