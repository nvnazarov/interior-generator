import "./NameInput.scss";
import { useCallback, type ChangeEvent } from "react";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { planUndoablyChanged, selectPlanEditor } from "./slice";

export function NameInput() {
  const dispatch = useAppDispatch();
  const name = useAppSelector((state) => selectPlanEditor(state).plan?.name);

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    dispatch(planUndoablyChanged({ name: e.target.value.slice(0, 256) }));
  }, []);

  return (
    <input
      className="plan-editor__name-input"
      onChange={handleChange}
      value={name}
      placeholder="Untitled plan"
    />
  );
}
