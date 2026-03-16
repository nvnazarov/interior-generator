import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { selectActiveTool, selectTool } from "../slice";
import { Icon } from "./Icon";
import "./ToolSelector.scss";

export function ToolSelector({
  tool,
  icon,
}: {
  tool: "wall" | "window" | "door" | "hand";
  icon: string;
}) {
  const dispatch = useAppDispatch();
  const activeTool = useAppSelector(selectActiveTool);
  return (
    <button
      className={
        activeTool === tool ? " tool-selector__active" : "tool-selector"
      }
      onClick={() => dispatch(selectTool(tool))}
    >
      <Icon src={icon} />
    </button>
  );
}
