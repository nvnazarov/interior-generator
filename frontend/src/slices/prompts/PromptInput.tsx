import {
  useCallback,
  type ChangeEvent,
  type MouseEvent,
  type SetStateAction,
} from "react";
import "./PromptInput.scss";
import {
  useGetAllPlansInProjectQuery,
  useGetPlanByIdQuery,
} from "../api/slice";
import { useContextMenu } from "../../shared/hooks/contextMenu";

function PlanName({ planId }: { planId: string }) {
  const { data } = useGetPlanByIdQuery(planId);
  return <>{data?.name}</>;
}

export function PromptInput({
  projectId,
  count,
  setCount,
  text,
  setText,
  basePlanId,
  setBasePlanId,
}: {
  projectId: string;
  basePlanId: string | null;
  text: string;
  setText: (text: SetStateAction<string>) => void;
  setBasePlanId: (id: SetStateAction<string | null>) => void;
  count: number;
  setCount: (count: SetStateAction<number>) => void;
}) {
  const menu = useContextMenu();
  const { data } = useGetAllPlansInProjectQuery(projectId);

  const handleTextChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      setText(e.target.value.slice(0, 512));
    },
    [setText],
  );

  const handleCountChange = useCallback(() => {
    setCount((count) => (count % 5) + 1);
  }, [setCount]);

  const handleBasePlanSelect = useCallback(
    (e: MouseEvent<HTMLSpanElement>) => {
      menu.show({
        x: e.clientX,
        y: e.clientY,
        items: [
          {
            name: "-",
            onClick: () => setBasePlanId(null),
          },
        ].concat(
          (data || []).map((plan) => ({
            name: plan.name,
            onClick: () => setBasePlanId(plan.id),
          })),
        ),
      });
    },
    [data],
  );

  return (
    <div className="prompts__prompt-input">
      <textarea
        placeholder="Type your thoughts..."
        value={text}
        onChange={handleTextChange}
      />
      <div>
        <span onClick={handleBasePlanSelect}>
          <p>Base</p> {basePlanId ? <PlanName planId={basePlanId} /> : "-"}
        </span>
        <span onClick={handleCountChange}>
          <p>Count</p> {count}
        </span>
      </div>
    </div>
  );
}
