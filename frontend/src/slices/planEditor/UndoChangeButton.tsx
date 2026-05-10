import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { changeUndone, selectCanUndoChange } from "./slice";
import { Tooltip } from "../../shared/components/tooltip/Tooltip";

export function UndoChangeButton() {
  const dispatch = useAppDispatch();
  const canUndoChange = useAppSelector(selectCanUndoChange);

  const handleClick = useCallback(() => {
    dispatch(changeUndone());
  }, []);

  return (
    <Tooltip content="Undo the last change" position="bottom">
      <Button icon="undo.png" onClick={handleClick} disabled={!canUndoChange} />
    </Tooltip>
  );
}
