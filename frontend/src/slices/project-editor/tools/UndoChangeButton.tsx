import { useCallback } from "react";
import { Button } from "../../../shared/components/button/Button";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { changeUndone, selectCanUndoChange } from "../slice";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function UndoChangeButton() {
  const dispatch = useAppDispatch();
  const canUndoChange = useAppSelector(selectCanUndoChange);

  const handleClick = useCallback(() => {
    dispatch(changeUndone());
  }, []);

  return (
    <Tooltip content={<p style={{ fontWeight: 400 }}>Undo change</p>}>
      <Button icon="undo.png" onClick={handleClick} disabled={!canUndoChange} />
    </Tooltip>
  );
}
