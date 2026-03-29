import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { selectPlanEditorTool, toolSelected } from "./slice";

export function SelectToolButton({
  icon,
  tool,
}: {
  icon: string;
  tool: "hand" | "area" | "furniture";
}) {
  const dispatch = useAppDispatch();
  const selectedTool = useAppSelector(selectPlanEditorTool);

  const handleClick = useCallback(() => {
    dispatch(toolSelected(tool));
  }, [tool]);

  return (
    <Button icon={icon} onClick={handleClick} active={tool === selectedTool} />
  );
}
