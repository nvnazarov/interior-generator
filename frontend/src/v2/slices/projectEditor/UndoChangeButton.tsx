import { useCallback } from "react";
import { Button } from "../../shared/components";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { changeUndone, selectCanUndoChange } from "./slice";

export function UndoChangeButton() {
  const dispatch = useAppDispatch();
  const canUndoChange = useAppSelector(selectCanUndoChange);

  const handleClick = useCallback(() => {
    dispatch(changeUndone());
  }, []);

  return (
    <Button icon="undo.png" onClick={handleClick} disabled={!canUndoChange} />
  );
}
