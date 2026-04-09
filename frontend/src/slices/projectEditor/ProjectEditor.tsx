import "./ProjectEditor.scss";
import { useEffect } from "react";
import { useLazyGetProjectByIdQuery } from "../api/slice";
import { RedoChangeButton } from "./RedoChangeButton";
import { SaveButton } from "./SaveButton";
import { UndoChangeButton } from "./UndoChangeButton";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { projectOpened, selectIsChatOpen } from "./slice";
import { Button, ContextMenuProvider } from "../../shared/components";
import { Scene } from "./Scene";
import { ChangeViewButton } from "./ChangeViewButton";
import { SelectToolButton } from "./SelectToolButton";
import { MenuButton } from "./MenuButton";
import { NameInput } from "./NameInput";
import { ChatButton } from "./ChatButton";
import { Chat } from "../prompts/Chat";

export function ProjectEditor({ projectId }: { projectId: string }) {
  const [getProjectById, { error }] = useLazyGetProjectByIdQuery();
  const dispatch = useAppDispatch();
  const isChatOpen = useAppSelector(selectIsChatOpen);

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
          <NameInput />
        </div>
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
        <div>
          <ChatButton />
        </div>
      </div>
      {isChatOpen && <Chat projectId={projectId} />}
      <Scene />
    </ContextMenuProvider>
  );
}
