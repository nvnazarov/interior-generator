import { useCallback, useState } from "react";
import { Button } from "../../shared/components";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { projectSaved, selectProjectEditor } from "./slice";
import { usePatchProjectMutation } from "../api/slice";

export function SaveButton() {
  const dispatch = useAppDispatch();
  const editor = useAppSelector(selectProjectEditor);
  const [patchProject] = usePatchProjectMutation();
  const [isSaving, setIsSaving] = useState(false);

  const handleClick = useCallback(async () => {
    if (!editor.project) {
      return;
    }
    try {
      setIsSaving(true);
      const revision = await patchProject({
        id: editor.project.id,
        revision: editor.project.revision,
        patch: editor.unsavedAccumulatedPatch,
      }).unwrap();
      dispatch(projectSaved(revision));
    } catch {
      // TODO
    } finally {
      setIsSaving(false);
    }
  }, [
    editor.project?.id,
    editor.project?.revision,
    editor.unsavedAccumulatedPatch,
  ]);

  return <Button title="Save" onClick={handleClick} disabled={isSaving} />;
}
