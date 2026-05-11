import { useCallback, type ReactNode } from "react";
import { Toggle } from "../../../shared/components/toggle/Toggle";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import {
  selectPlanEditorTool,
  toolSelected,
  type PlanEditorState,
} from "../slice";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function SelectToolButton({
  icon,
  tool,
  tooltip,
}: {
  icon: string;
  tool: PlanEditorState["tool"];
  tooltip?: ReactNode;
}) {
  const dispatch = useAppDispatch();
  const selectedTool = useAppSelector(selectPlanEditorTool);

  const handleChange = useCallback(() => {
    dispatch(toolSelected(tool));
  }, [tool]);

  return (
    <Tooltip content={tooltip}>
      <Toggle
        icon={icon}
        onChange={handleChange}
        checked={tool === selectedTool}
      />
    </Tooltip>
  );
}
