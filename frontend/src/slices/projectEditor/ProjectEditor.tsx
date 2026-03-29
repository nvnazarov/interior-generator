import "./ProjectEditor.scss";
import { useEffect } from "react";
import { useLazyGetProjectByIdQuery } from "../api/slice";
import { RedoChangeButton } from "./RedoChangeButton";
import { SaveButton } from "./SaveButton";
import { UndoChangeButton } from "./UndoChangeButton";
import { useAppDispatch } from "../storeTypes";
import { projectOpened } from "./slice";
import { Button, ContextMenuProvider } from "../../shared/components";
import { Scene } from "./Scene";
import { ChangeViewButton } from "./ChangeViewButton";
import { SelectToolButton } from "./SelectToolButton";
import { MenuButton } from "./MenuButton";

export function ProjectEditor({ projectId }: { projectId: string }) {
  const [getProjectById, { error }] = useLazyGetProjectByIdQuery();
  const dispatch = useAppDispatch();

  useEffect(() => {
    async function loadProject() {
      const project = await getProjectById(projectId).unwrap();
      dispatch(projectOpened(project));
    }
    loadProject();
  }, []);

  if (error) {
    return (
      <>
        <Button title="Refresh" />
      </>
    );
  }

  return (
    <ContextMenuProvider>
      <div className="project-editor__project-editor__menu">
        <div>
          <MenuButton projectId={projectId} />
        </div>
        <span />
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
        <span />
      </div>
      <Scene />
    </ContextMenuProvider>
  );
}
