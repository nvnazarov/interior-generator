import { useCallback, useState } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import {
  projectSaved,
  selectIsProjectSaved,
  selectProjectEditor,
} from "./slice";
import { usePatchProjectMutation } from "../api/slice";
import { useTranslation } from "react-i18next";

export function SaveButton() {
  const dispatch = useAppDispatch();
  const editor = useAppSelector(selectProjectEditor);
  const isProjectSaved = useAppSelector(selectIsProjectSaved);
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

  return (
    <Button
      icon="sync.png"
      onClick={handleClick}
      loading={isSaving}
      disabled={isProjectSaved}
    />
  );
}
