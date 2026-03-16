import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { redo, selectCanRedo } from "../slice";
import { Icon } from "./Icon";
import "./RedoButton.scss";

export function RedoButton() {
  const dispatch = useAppDispatch();
  const canRedo = useAppSelector(selectCanRedo);
  return (
    <button
      className={canRedo ? "redo-button" : "redo-button__disabled"}
      onClick={() => dispatch(redo())}
      disabled={!canRedo}
    >
      <Icon src="icons/redo.png" />
    </button>
  );
}
