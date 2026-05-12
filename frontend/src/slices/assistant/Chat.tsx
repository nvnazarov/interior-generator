import moment from "moment";
import type { Prompt as PromptEntity } from "../api/entities";
import {
  useGeneratePlansMutation,
  useLazyGetPromptsForProjectQuery,
  usePatchPlanMutation,
  usePatchProjectMutation,
} from "../api/slice";
import "./Chat.scss";
import { useCallback, useEffect, useState } from "react";
import { v4 } from "uuid";
import { PromptInput } from "./PromptInput";
import { Spinner } from "../../shared/components";
import { Prompt } from "./Prompt";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { notify } from "../notifications/slice";
import { Button } from "../../shared/components/button/Button";
import { motion } from "motion/react";
import { planSaved, selectPlanEditor } from "../plan-editor/slice";
import { projectSaved, selectProjectEditor } from "../project-editor/slice";

export function Chat({ projectId }: { projectId: string }) {
  const dispatch = useAppDispatch();
  const [count, setCount] = useState(1);
  const [text, setText] = useState("");
  const [basePlanId, setBasePlanId] = useState<string | null>(null);
  const [patchPlan] = usePatchPlanMutation();
  const [patchProject] = usePatchProjectMutation();
  const planEditor = useAppSelector(selectPlanEditor);
  const projectEditor = useAppSelector(selectProjectEditor);

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

      if (projectEditor.project) {
        const revision = await patchProject({
          id: projectEditor.project.id,
          revision: projectEditor.project.revision,
          patch: projectEditor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(projectSaved(revision));
      }

      if (planEditor.plan) {
        const revision = await patchPlan({
          id: planEditor.plan.id,
          revision: planEditor.plan.revision,
          patch: planEditor.unsavedAccumulatedPatch,
        }).unwrap();
        dispatch(planSaved(revision));
      }

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
    <motion.div
      className="chat"
      initial={{ rotateY: 90 }}
      animate={{ rotateY: 0 }}
      exit={{ rotateY: 90, transition: { ease: "easeIn", duration: 0.125 } }}
    >
      {isLoading ? (
        <div className="chat__loading">
          <Spinner />
        </div>
      ) : isSuccess ? (
        <div className="chat__history">
          {prompts.map((prompt) => (
            <Prompt
              key={prompt.id}
              prompt={prompt}
              onAfterDeleted={handlePromptDeleted}
            />
          ))}
        </div>
      ) : (
        <div className="chat__history">Unable to load chat history</div>
      )}
      <div className="chat__input">
        <PromptInput
          projectId={projectId}
          text={text}
          setText={setText}
          count={count}
          setCount={setCount}
          basePlanId={basePlanId}
          setBasePlanId={setBasePlanId}
        />
        <Button
          onClick={handleGenerate}
          disabled={isBusy || text.length === 0}
          loading={isBusy}
          primary
          text="Generate"
        />
      </div>
    </motion.div>
  );
}
