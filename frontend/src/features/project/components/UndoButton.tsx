import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { selectCanUndo, undo } from "../slice";
import { Icon } from "./Icon";
import "./UndoButton.scss";

export function UndoButton() {
  const dispatch = useAppDispatch();
  const canUndo = useAppSelector(selectCanUndo);
  return (
    <button
      className={canUndo ? "undo-button" : "undo-button__disabled"}
      onClick={() => dispatch(undo())}
      disabled={!canUndo}
    >
      <Icon src="icons/undo.png" />
    </button>
  );
}
