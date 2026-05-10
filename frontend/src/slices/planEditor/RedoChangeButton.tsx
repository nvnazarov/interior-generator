import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { changeRedone, selectCanRedoChange } from "./slice";
import { Tooltip } from "../../shared/components/tooltip/Tooltip";

export function RedoChangeButton() {
  const dispatch = useAppDispatch();
  const canRedoChange = useAppSelector(selectCanRedoChange);

  const handleClick = useCallback(() => {
    dispatch(changeRedone());
  }, []);

  return (
    <Tooltip content="Redo the last undone change" position="bottom">
      <Button icon="redo.png" onClick={handleClick} disabled={!canRedoChange} />
    </Tooltip>
  );
}
