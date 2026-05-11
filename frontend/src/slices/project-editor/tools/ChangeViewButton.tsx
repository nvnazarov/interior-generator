import { useCallback } from "react";
import { Button } from "../../../shared/components/button/Button";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { selectProjectEditorView, viewChanged } from "../slice";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function ChangeViewButton() {
  const dispatch = useAppDispatch();
  const view = useAppSelector(selectProjectEditorView);

  const handleClick = useCallback(() => {
    dispatch(viewChanged(view === "2D" ? "3D" : "2D"));
  }, [view]);

  return (
    <Tooltip
      content={
        <p style={{ fontWeight: 400 }}>
          Change view (<b>2D</b> or <b>3D</b>). Note that controls are slightly
          different in these modes.
        </p>
      }
    >
      <Button text={view} onClick={handleClick} />
    </Tooltip>
  );
}
