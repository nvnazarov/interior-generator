import moment from "moment";
import type { Prompt } from "../api/entities";
import {
  useDeletePromptMutation,
  useGeneratePlansMutation,
  useLazyGetPromptsForProjectQuery,
} from "../api/slice";
import "./Chat.scss";
import { Link } from "react-router";
import { useCallback, useEffect, useState, type ChangeEvent } from "react";
import { human } from "./lib";
import { v4 } from "uuid";

function PromptComponent({
  prompt,
  onDelete,
}: {
  prompt: Prompt;
  onDelete: (promptId: string) => void;
}) {
  const [deletePrompt] = useDeletePromptMutation();

  const handleDeletePrompt = useCallback(async () => {
    await deletePrompt(prompt.id)
      .unwrap()
      .then(() => onDelete(prompt.id));
  }, [prompt.id]);

  const classes = ["prompts__chat__prompt"];
  switch (prompt.status) {
    case "pending": {
      classes.push("prompts__chat__prompt__pending");
      break;
    }
    case "failed": {
      classes.push("prompts__chat__prompt__failed");
      break;
    }
  }
  return (
    <div className={classes.join(" ")}>
      <div>
        <p>{prompt.text}</p>
        <button onClick={handleDeletePrompt}>
          <img src="/app/icons/trash.png" />
        </button>
      </div>
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
        </>
      )}
      <div>
        <span>{moment(prompt.dtCreated).fromNow()}</span>
        {prompt.status === "success" ? (
          <span>{human(moment(prompt.dtDone!).diff(prompt.dtCreated))}</span>
        ) : prompt.status === "pending" ? (
          <span className="prompts__chat__loader"></span>
        ) : (
          prompt.status === "failed" && <span>FAILED</span>
        )}
      </div>
    </div>
  );
}

export function Chat({ projectId }: { projectId: string }) {
  const [text, setText] = useState("");
  const [getPromptsForProject, { isSuccess }] =
    useLazyGetPromptsForProjectQuery();
  const [generatePlans] = useGeneratePlansMutation();
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    getPromptsForProject(projectId, true)
      .unwrap()
      .then((loadedPrompts) => setPrompts(loadedPrompts));
  }, [projectId]);

  const handleGenerate = useCallback(async () => {
    try {
      setIsBusy(true);
      setText("");
      const placeholderId = v4();
      setPrompts((prompts) => [
        ...prompts,
        {
          id: placeholderId,
          projectId,
          text,
          basePlanId: null,
          dtCreated: moment().toISOString(),
          status: "pending",
        } as Prompt,
      ]);
      await generatePlans({
        projectId,
        text,
        basePlanId: null,
        count: 5,
      })
        .unwrap()
        .then((prompt) =>
          setPrompts((prompts) => [
            ...prompts.filter((p) => p.id !== placeholderId),
            prompt,
          ]),
        );
    } finally {
      setIsBusy(false);
    }
  }, [projectId, text]);

  const handleTextChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      setText(e.target.value);
    },
    [],
  );

  const handlePromptDeleted = useCallback((promptId: string) => {
    setPrompts((prompts) => prompts.filter((p) => p.id !== promptId));
  }, []);

  return (
    <div className="prompts__chat">
      {isSuccess ? (
        <div className="prompts__chat__history">
          {prompts.map((prompt) => (
            <PromptComponent
              key={prompt.id}
              prompt={prompt}
              onDelete={handlePromptDeleted}
            />
          ))}
        </div>
      ) : (
        <p>Unable to load chat history</p>
      )}
      <div className="prompts__chat__input">
        <textarea
          placeholder="Type your thoughts..."
          value={text}
          onChange={handleTextChange}
        />
        <button onClick={handleGenerate} disabled={isBusy}>
          Generate
        </button>
      </div>
    </div>
  );
}
