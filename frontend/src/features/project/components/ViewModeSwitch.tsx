import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { selectProjectEditor, switchViewMode } from "../slice";
import "./ViewModeSwitch.scss";

export function ViewModeSwitch() {
  const dispatch = useAppDispatch();
  const editor = useAppSelector(selectProjectEditor);
  function handleClick() {
    dispatch(switchViewMode());
  }
  return (
    <button className="view-mode-switch" onClick={handleClick}>
      {editor.viewMode}
    </button>
  );
}
