import { useCallback } from "react";
import { Button } from "../../shared/components";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { changeRedone, selectCanRedoChange } from "./slice";

export function RedoChangeButton() {
  const dispatch = useAppDispatch();
  const canRedoChange = useAppSelector(selectCanRedoChange);

  const handleClick = useCallback(() => {
    dispatch(changeRedone());
  }, []);

  return (
    <Button icon="redo.png" onClick={handleClick} disabled={!canRedoChange} />
  );
}
