import moment from "moment";
import { useCallback, useState } from "react";

import "./Prompt.scss";
import type { PlanPatch, Prompt } from "../api/entities";
import { human } from "./lib";
import { Button, Spinner, Tooltip } from "../../shared/components";
import { useDeletePromptMutation } from "../api/slice";
import { useAppDispatch } from "../storeTypes";
import { planChangedTo } from "../plan-editor/slice";
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
    const plan = applyJsonMergePatch(
      prompt.base ?? {
        furniture: {},
        areas: {},
      },
      patch.content,
    );
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
    <div className="prompt">
      <div className="prompt__body">
        <p>{prompt.text}</p>
        <Tooltip content={<p style={{ fontWeight: 400 }}>Delete prompt</p>}>
          <Button
            onClick={handleDeletion}
            icon="trash.png"
            disabled={isDeleting || prompt.status === "pending"}
            style={{ width: "28px", height: "28px" }}
          />
        </Tooltip>
      </div>
      <div className="prompt__result">
        {prompt.base !== null && (
          <Tooltip
            content={
              <p style={{ fontWeight: 400 }}>
                Change current plan to the base plan selected before the
                generation
              </p>
            }
          >
            <Button text="Base" onClick={() => handleShowBase()} />
          </Tooltip>
        )}
        {prompt.status === "success" && (
          <>
            {prompt.patches.map((patch, idx) => (
              <Button
                text={`P${idx + 1}`}
                key={idx}
                primary
                onClick={() => handleShowPlan(patch)}
                style={{ width: "34px" }}
              />
            ))}
          </>
        )}
      </div>
      <div className="prompt__status-bar">
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
