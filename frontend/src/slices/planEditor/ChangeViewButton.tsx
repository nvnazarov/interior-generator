import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { selectPlanEditorView, viewChanged } from "./slice";
import { Tooltip } from "../../shared/components/tooltip/Tooltip";

export function ChangeViewButton() {
  const dispatch = useAppDispatch();
  const view = useAppSelector(selectPlanEditorView);

  const handleClick = useCallback(() => {
    dispatch(viewChanged(view === "2D" ? "3D" : "2D"));
  }, [view]);

  return (
    <Tooltip
      content={
        <>
          Change the view to <b>{view === "2D" ? "3D" : "2D"}</b>
        </>
      }
    >
      <Button title={view} onClick={handleClick} />
    </Tooltip>
  );
}
