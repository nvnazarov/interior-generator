import { useState } from "react";
import { useAppDispatch } from "../../../app/hooks";
import { createPlan } from "../thunks";
import { Icon } from "./Icon";
import "./AddPlanButton.scss";

export function AddPlanButton({ projectId }: { projectId: string }) {
  const dispatch = useAppDispatch();
  const [isCreating, setIsCreating] = useState(false);

  function handleClick() {
    if (isCreating) return;
    setIsCreating(true);
    dispatch(createPlan(projectId)).finally(() => setIsCreating(false));
  }

  return (
    <button
      className="add-plan-button"
      onClick={handleClick}
      disabled={isCreating}
    >
      <Icon src="icons/plus.png" />
    </button>
  );
}
