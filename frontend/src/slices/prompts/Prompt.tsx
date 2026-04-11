import "./Prompt.scss";
import type { Prompt } from "../api/entities";
import moment from "moment";
import { human } from "./lib";
import { Link } from "react-router";
import { Spinner } from "../../shared/components";
import { useCallback, useState } from "react";
import { useDeletePromptMutation } from "../api/slice";

export function Prompt({
  prompt,
  onAfterDeleted,
}: {
  prompt: Prompt;
  onAfterDeleted: (id: string) => void;
}) {
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

  return (
    <div className="prompts__prompt">
      <div>
        <p>{prompt.text}</p>
        <button onClick={handleDeletion} disabled={isDeleting}>
          <img src="/app/icons/trash.png" />
        </button>
      </div>
      <div>
        {prompt.basePlanId !== null && (
          <Link
            to={`/editor/projects/${prompt.projectId}/plans/${prompt.basePlanId}`}
          >
            Base
          </Link>
        )}
        {prompt.status === "success" && (
          <div>
            {prompt.generatedPlansIds.map((planId, idx) => (
              <Link
                key={idx}
                to={`/editor/project/${prompt.projectId}/plan/${planId}`}
              >
                P{idx + 1}
              </Link>
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
              Failed after {human(moment(prompt.dtDone!).diff(prompt.dtCreated))}
            </div>
          )
        )}
      </div>
    </div>
  );
}
