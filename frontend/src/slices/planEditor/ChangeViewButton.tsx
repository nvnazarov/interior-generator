import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { selectPlanEditorView, viewChanged } from "./slice";

export function ChangeViewButton() {
  const dispatch = useAppDispatch();
  const view = useAppSelector(selectPlanEditorView);

  const handleClick = useCallback(() => {
    dispatch(viewChanged(view === "2D" ? "3D" : "2D"));
  }, [view]);

  return <Button title={view} onClick={handleClick} />;
}
