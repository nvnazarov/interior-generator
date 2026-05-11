import { useCallback, type ChangeEvent } from "react";

import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { planUndoablyChanged, selectPlanEditor } from "../slice";
import { TextInput } from "../../../shared/components/input/TextInput";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function NameInput() {
  const dispatch = useAppDispatch();
  const name = useAppSelector((state) => selectPlanEditor(state).plan?.name);

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    dispatch(planUndoablyChanged({ name: e.target.value.slice(0, 256) }));
  }, []);

  return (
    <Tooltip
      content={
        <p style={{ fontWeight: 400 }}>
          <b>Project title:</b> {name ? `${name}` : "untitled"}
        </p>
      }
    >
      <TextInput
        onChange={handleChange}
        value={name}
        placeholder="Untitled plan"
        maxLength={256}
      />
    </Tooltip>
  );
}
