import moment from "moment";
import type { Prompt } from "../api/entities";
import {
  useGeneratePlansMutation,
  useGetPromptsForProjectQuery,
} from "../api/slice";
import "./Chat.scss";
import { Link } from "react-router";
import { useCallback, useState, type ChangeEvent } from "react";

function PromptComponent({ prompt }: { prompt: Prompt }) {
  return (
    <div className="prompts__chat__prompt">
      <p>{prompt.text}</p>
      {prompt.status === "success" && (
        <>
          <div>
            {prompt.basePlanId && (
              <>
                <Link
                  to={`/editor/projects/${prompt.projectId}/plans/${prompt.basePlanId}`}
                >
                  Base plan
                </Link>
                <div></div>
              </>
            )}
            {prompt.generatedPlansIds.map((idx, planId) => (
              <Link
                key={idx}
                to={`/editor/projects/${prompt.projectId}/plans/${planId}`}
              >
                {idx + 1}
              </Link>
            ))}
          </div>
          <span>{moment(prompt.dtCreated).fromNow()}</span>
          <span>{moment(prompt.dtDone!).diff(prompt.dtCreated)}</span>
        </>
      )}
      {prompt.status === "failed" && <span>Failed</span>}
      {prompt.status === "pending" && <span>Loading</span>}
    </div>
  );
}

export function Chat({ projectId }: { projectId: string }) {
  const [text, setText] = useState("");
  const { data, isSuccess } = useGetPromptsForProjectQuery(projectId);
  const [generatePlans] = useGeneratePlansMutation();

  const handleClick = useCallback(async () => {
    await generatePlans({ projectId, text, basePlanId: null }).unwrap();
  }, [projectId, text]);

  const handleTextChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setText(e.target.value);
  }, []);

  return (
    <div className="prompts__chat">
      {isSuccess && data.map((prompt) => <PromptComponent prompt={prompt} />)}
      <div>
        <input
          placeholder="Type your thoughts..."
          value={text}
          onChange={handleTextChange}
        />
        <button onClick={handleClick}>Generate</button>
      </div>
    </div>
  );
}
