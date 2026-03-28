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
import { ChangeViewButton } from "./ChangeViewButton";
import { SelectToolButton } from "./SelectToolButton";

export function ProjectEditor({ projectId }: { projectId: string }) {
  const [getProjectById, { error }] = useLazyGetProjectByIdQuery();
  const dispatch = useAppDispatch();

  const loadProject = useCallback(async () => {
    const project = await getProjectById(projectId, true).unwrap();
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
        <div>
          <SelectToolButton icon="hand.png" tool="hand" />
          <SelectToolButton icon="wall.png" tool="wall" />
          <SelectToolButton icon="window.png" tool="window" />
          <SelectToolButton icon="door.png" tool="door" />
          <SelectToolButton icon="raindrops.png" tool="wet_area" />
        </div>
        <div>
          <ChangeViewButton />
        </div>
        <div>
          <UndoChangeButton />
          <RedoChangeButton />
        </div>
        <div>
          <SaveButton />
        </div>
      </div>
      <Scene />
    </>
  );
}
