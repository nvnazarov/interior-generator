import type { ChangeEvent } from "react";
import { useAppSelector } from "../../../app/hooks";
import { selectPlansByProjectId } from "../../plan/slice";
import { useNavigate } from "react-router";

export function EditorSelector({ projectId }: { projectId: string }) {
  const navigate = useNavigate();
  const plans = useAppSelector(selectPlansByProjectId(projectId));

  function handleChange(e: ChangeEvent<HTMLSelectElement>) {
    const selectedOption = e.target.value;
    if (selectedOption === "") {
      navigate(`/projects/${projectId}`);
    } else {
      navigate(`/projects/${projectId}/plans/${selectedOption}`);
    }
  }

  return (
    <select onChange={handleChange}>
      <option value="">Select Plan</option>
      {plans.map((plan) => (
        <option value={plan.id}>{plan.name}</option>
      ))}
    </select>
  );
}
