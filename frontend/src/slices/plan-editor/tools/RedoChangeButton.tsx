import { useCallback } from "react";
import { Button } from "../../../shared/components/button/Button";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { changeRedone, selectCanRedoChange } from "../slice";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function RedoChangeButton() {
  const dispatch = useAppDispatch();
  const canRedoChange = useAppSelector(selectCanRedoChange);

  const handleClick = useCallback(() => {
    dispatch(changeRedone());
  }, []);

  return (
    <Tooltip content={<p style={{ fontWeight: 400 }}>Redo change</p>}>
      <Button icon="redo.png" onClick={handleClick} disabled={!canRedoChange} />
    </Tooltip>
  );
}
