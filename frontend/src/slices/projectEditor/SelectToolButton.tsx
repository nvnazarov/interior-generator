import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { selectProjectEditorTool, toolSelected } from "./slice";

export function SelectToolButton({
  icon,
  tool,
}: {
  icon: string;
  tool: "hand" | "window" | "door" | "wall" | "wet_area";
}) {
  const dispatch = useAppDispatch();
  const selectedTool = useAppSelector(selectProjectEditorTool);

  const handleClick = useCallback(() => {
    dispatch(toolSelected(tool));
  }, [tool]);

  return (
    <Button icon={icon} onClick={handleClick} active={tool === selectedTool} />
  );
}
