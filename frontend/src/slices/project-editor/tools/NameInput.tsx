import { useCallback, type ChangeEvent } from "react";

import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { projectUndoablyChanged, selectProjectEditor } from "../slice";
import { TextInput } from "../../../shared/components/input/TextInput";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function NameInput() {
  const dispatch = useAppDispatch();
  const name = useAppSelector(
    (state) => selectProjectEditor(state).project?.name,
  );

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    dispatch(projectUndoablyChanged({ name: e.target.value.slice(0, 256) }));
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
        placeholder="Untitled project"
        maxLength={256}
      />
    </Tooltip>
  );
}
