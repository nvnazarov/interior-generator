import { useCallback, type ReactNode } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { selectPlanEditorTool, toolSelected } from "./slice";
import { Tooltip } from "../../shared/components/tooltip/Tooltip";

export function SelectToolButton({
  icon,
  tool,
  tooltip,
}: {
  icon: string;
  tool: "hand" | "area" | "furniture";
  tooltip: ReactNode;
}) {
  const dispatch = useAppDispatch();
  const selectedTool = useAppSelector(selectPlanEditorTool);

  const handleClick = useCallback(() => {
    dispatch(toolSelected(tool));
  }, [tool]);

  return (
    <Tooltip content={tooltip}>
      <Button
        icon={icon}
        onClick={handleClick}
        active={tool === selectedTool}
      />
    </Tooltip>
  );
}
