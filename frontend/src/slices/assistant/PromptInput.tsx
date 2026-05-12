import { useCallback, type ChangeEvent, type SetStateAction } from "react";
import "./PromptInput.scss";
import { useGetAllPlansInProjectQuery } from "../api/slice";
import { Button } from "../../shared/components/button/Button";
import {
  ContextMenu,
  ContextMenuOption,
  Tooltip,
} from "../../shared/components";

export function PromptInput({
  basePlanId,
  projectId,
  count,
  setCount,
  text,
  setText,
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

  const plan = data?.find((p) => p.id === basePlanId);

  return (
    <div className="prompt-input">
      <textarea
        placeholder="Type your thoughts..."
        value={text}
        onChange={handleTextChange}
      />
      <div className="prompt-input__options">
        <ContextMenu
          content={
            <>
              <ContextMenuOption
                text="none"
                onClick={() => setBasePlanId(null)}
              />
              {(data || []).map((plan, idx) => (
                <ContextMenuOption
                  key={plan.id}
                  text={`${idx}. ` + (plan.name || "Untitled plan")}
                  onClick={() => setBasePlanId(plan.id)}
                />
              ))}
            </>
          }
        >
          <Button
            text={`Base: ${plan ? plan.name || "Untitled plan" : "..."}`}
          />
        </ContextMenu>
        <Tooltip
          content={
            <p style={{ fontWeight: 400 }}>
              Select number of plans to generate
            </p>
          }
        >
          <Button onClick={handleCountChange} text={`Count: ${count}`} />
        </Tooltip>
      </div>
    </div>
  );
}
