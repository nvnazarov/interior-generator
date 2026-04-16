import "./Prompt.scss";
import type { PlanPatch, Prompt } from "../api/entities";
import moment from "moment";
import { human } from "./lib";
import { Spinner } from "../../shared/components";
import { useCallback, useState } from "react";
import { useDeletePromptMutation } from "../api/slice";
import { useAppDispatch } from "../storeTypes";
import { planChangedTo } from "../planEditor/slice";
import { applyJsonMergePatch } from "../../shared/lib/jsonMergePatch";

export function Prompt({
  prompt,
  onAfterDeleted,
}: {
  prompt: Prompt;
  onAfterDeleted: (id: string) => void;
}) {
  const dispatch = useAppDispatch();
  const [deletePrompt] = useDeletePromptMutation();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeletion = useCallback(async () => {
    try {
      setIsDeleting(true);
      await deletePrompt(prompt.id)
        .unwrap()
        .then(() => onAfterDeleted(prompt.id));
    } finally {
      setIsDeleting(false);
    }
  }, []);

  const handleShowBase = useCallback(() => {
    if (prompt.base) {
      dispatch(planChangedTo(prompt.base));
    }
  }, []);

  const handleShowPlan = useCallback((patch: PlanPatch) => {
    const plan = applyJsonMergePatch(prompt.base, patch);
    dispatch(
      planChangedTo(
        plan !== null
          ? plan
          : {
              areas: {},
              furniture: {},
            },
      ),
    );
  }, []);

  return (
    <div className="prompts__prompt">
      <div>
        <p>{prompt.text}</p>
        <button onClick={handleDeletion} disabled={isDeleting}>
          <img src="/app/icons/trash.png" />
        </button>
      </div>
      <div>
        {prompt.base !== null && (
          <span onClick={() => handleShowBase()}>Base</span>
        )}
        {prompt.status === "success" && (
          <div>
            {prompt.patches.map((patch, idx) => (
              <span key={idx} onClick={() => handleShowPlan(patch)}>
                P{idx + 1}
              </span>
            ))}
          </div>
        )}
      </div>
      <div>
        <div>{moment(prompt.dtCreated).fromNow()}</div>
        {prompt.status === "success" ? (
          <div>{human(moment(prompt.dtDone!).diff(prompt.dtCreated))}</div>
        ) : prompt.status === "pending" ? (
          <Spinner />
        ) : (
          prompt.status === "failed" && (
            <div>
              Failed after{" "}
              {human(moment(prompt.dtDone!).diff(prompt.dtCreated))}
            </div>
          )
        )}
      </div>
    </div>
  );
}
