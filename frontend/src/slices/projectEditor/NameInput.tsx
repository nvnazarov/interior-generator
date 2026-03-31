import "./NameInput.scss";
import { useCallback, type ChangeEvent } from "react";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { projectUndoablyChanged, selectProjectEditor } from "./slice";

export function NameInput() {
  const dispatch = useAppDispatch();
  const name = useAppSelector(
    (state) => selectProjectEditor(state).project?.name,
  );

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    dispatch(projectUndoablyChanged({ name: e.target.value.slice(0, 256) }));
  }, []);

  return (
    <input
      className="project-editor__name-input"
      onChange={handleChange}
      value={name}
      placeholder="Untitled project"
    />
  );
}
