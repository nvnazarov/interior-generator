import { useCallback, useState } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { planSaved, selectIsPlanSaved, selectPlanEditor } from "./slice";
import { usePatchPlanMutation } from "../api/slice";

export function SaveButton() {
  const dispatch = useAppDispatch();
  const editor = useAppSelector(selectPlanEditor);
  const isPlanSaved = useAppSelector(selectIsPlanSaved);
  const [patchPlan] = usePatchPlanMutation();
  const [isSaving, setIsSaving] = useState(false);

  const handleClick = useCallback(async () => {
    if (!editor.plan) {
      return;
    }
    try {
      setIsSaving(true);
      const revision = await patchPlan({
        id: editor.plan.id,
        revision: editor.plan.revision,
        patch: editor.unsavedAccumulatedPatch,
      }).unwrap();
      dispatch(planSaved(revision));
    } catch {
      // TODO
    } finally {
      setIsSaving(false);
    }
  }, [editor.plan?.id, editor.plan?.revision, editor.unsavedAccumulatedPatch]);

  return (
    <Button
      icon="sync.png"
      onClick={handleClick}
      loading={isSaving}
      disabled={isPlanSaved}
    />
  );
}
