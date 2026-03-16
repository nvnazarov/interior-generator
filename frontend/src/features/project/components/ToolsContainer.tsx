import type React from "react";
import "./ToolsContainer.scss";

export function ToolsContainer({ children }: { children?: React.ReactNode }) {
  return <div className="project__tools-container">{children}</div>;
}
