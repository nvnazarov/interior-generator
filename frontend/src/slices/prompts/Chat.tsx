import moment from "moment";
import type { Prompt as PromptEntity } from "../api/entities";
import {
  useGeneratePlansMutation,
  useLazyGetPromptsForProjectQuery,
} from "../api/slice";
import "./Chat.scss";
import { useCallback, useEffect, useState } from "react";
import { v4 } from "uuid";
import { PromptInput } from "./PromptInput";
import { Spinner } from "../../shared/components";
import { Prompt } from "./Prompt";
import { useAppDispatch } from "../storeTypes";
import { notify } from "../notifications/slice";

export function Chat({ projectId }: { projectId: string }) {
  const dispatch = useAppDispatch();
  const [count, setCount] = useState(1);
  const [text, setText] = useState("");
  const [basePlanId, setBasePlanId] = useState<string | null>(null);

  const [getPromptsForProject, { isLoading, isSuccess }] =
    useLazyGetPromptsForProjectQuery();
  const [generatePlans] = useGeneratePlansMutation();

  const [prompts, setPrompts] = useState<PromptEntity[]>([]);
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    getPromptsForProject(projectId, true)
      .unwrap()
      .then((loadedPrompts) => setPrompts(loadedPrompts));
  }, [projectId]);

  const handleGenerate = useCallback(async () => {
    const placeholderId = v4();
    try {
      setIsBusy(true);
      // TODO: sync plan
      setText("");
      setPrompts((prompts) => [
        ...prompts,
        {
          id: placeholderId,
          projectId,
          text,
          base: basePlanId
            ? {
                furniture: {},
                areas: {},
              }
            : null,
          patches: [],
          dtDone: null,
          dtCreated: moment().toISOString(),
          status: "pending",
        } as PromptEntity,
      ]);
      await generatePlans({
        projectId,
        text,
        basePlanId,
        count,
      })
        .unwrap()
        .then((prompt) =>
          setPrompts((prompts) => [
            ...prompts.filter((p) => p.id !== placeholderId),
            prompt,
          ]),
        );
    } catch {
      dispatch(notify({ text: "Something went wrong", severity: "error" }));
      setPrompts((prompts) =>
        prompts.map((p) =>
          p.id !== placeholderId ? p : { ...p, status: "failed" },
        ),
      );
    } finally {
      setIsBusy(false);
    }
  }, [projectId, text, basePlanId, count]);

  const handlePromptDeleted = useCallback((promptId: string) => {
    setPrompts((prompts) => prompts.filter((p) => p.id !== promptId));
  }, []);

  return (
    <div className="prompts__chat">
      {isLoading ? (
        <Spinner />
      ) : isSuccess ? (
        <div className="prompts__chat__history">
          {prompts.map((prompt) => (
            <Prompt
              key={prompt.id}
              prompt={prompt}
              onAfterDeleted={handlePromptDeleted}
            />
          ))}
        </div>
      ) : (
        <div className="prompts__chat__history">
          Unable to load chat history
        </div>
      )}
      <div className="prompts__chat__input">
        <PromptInput
          projectId={projectId}
          text={text}
          setText={setText}
          count={count}
          setCount={setCount}
          basePlanId={basePlanId}
          setBasePlanId={setBasePlanId}
        />
        <button onClick={handleGenerate} disabled={isBusy || text.length === 0}>
          Generate {isBusy && <Spinner />}
        </button>
      </div>
    </div>
  );
}
