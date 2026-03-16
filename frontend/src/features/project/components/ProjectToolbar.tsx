import "./ProjectToolbar.scss";
import { ToolSelector } from "./ToolSelector";
import { ViewModeSwitch } from "./ViewModeSwitch";

export function ProjectToolbar() {
  return (
    <div className="project__toolbar">
      <ToolSelector tool="hand" icon="icons/hand.png" />
      <ToolSelector tool="window" icon="icons/window.png" />
      <ToolSelector tool="door" icon="icons/door.png" />
      <ToolSelector tool="wall" icon="icons/wall.png" />
      <ViewModeSwitch />
    </div>
  );
}
