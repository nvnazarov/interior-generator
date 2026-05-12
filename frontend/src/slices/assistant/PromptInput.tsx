import { useCallback, type ChangeEvent, type SetStateAction } from "react";
import "./PromptInput.scss";
import { useGetAllPlansInProjectQuery } from "../api/slice";
import { Button } from "../../shared/components/button/Button";
import { ContextMenu, ContextMenuOption } from "../../shared/components";

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

  return (
    <div className="prompt-input">
      <textarea
        placeholder="Type your thoughts..."
        value={text}
        onChange={handleTextChange}
      />
      <div>
        <ContextMenu
          content={
            <>
              <ContextMenuOption
                text="none"
                onClick={() => setBasePlanId(null)}
              />
              {(data || []).map((plan) => (
                <ContextMenuOption
                  key={plan.id}
                  text={plan.name || plan.id.slice(0, 6)}
                  onClick={() => setBasePlanId(plan.id)}
                />
              ))}
            </>
          }
        >
          <Button text={`Base: ${0}`} />
        </ContextMenu>
        <Button onClick={handleCountChange} text={`Count: ${count}`} />
      </div>
    </div>
  );
}
