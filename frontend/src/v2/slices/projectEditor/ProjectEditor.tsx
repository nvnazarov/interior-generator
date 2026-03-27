import "./ProjectEditor.scss";
import { useCallback, useEffect } from "react";
import { useLazyGetProjectByIdQuery } from "../api/slice";
import { RedoChangeButton } from "./RedoChangeButton";
import { SaveButton } from "./SaveButton";
import { UndoChangeButton } from "./UndoChangeButton";
import { useAppDispatch } from "../storeTypes";
import { projectOpened } from "./slice";
import { Button } from "../../shared/components";
import { Scene } from "./Scene";

export function ProjectEditor({ projectId }: { projectId: string }) {
  const [getProjectById, { error }] = useLazyGetProjectByIdQuery();
  const dispatch = useAppDispatch();

  const loadProject = useCallback(async () => {
    const project = await getProjectById(projectId).unwrap();
    dispatch(projectOpened(project));
  }, [projectId]);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  if (error) {
    return (
      <>
        <Button title="Refresh" />
      </>
    );
  }

  return (
    <>
      <div className="project-editor__project-editor__menu">
        <UndoChangeButton />
        <RedoChangeButton />
        <SaveButton />
      </div>
      <Scene />
    </>
  );
}
