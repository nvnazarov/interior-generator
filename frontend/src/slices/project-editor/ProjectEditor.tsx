import { useEffect } from "react";

import "./ProjectEditor.scss";
import { useGetProjectByIdQuery } from "../api/slice";
import { RedoChangeButton } from "./tools/RedoChangeButton";
import { UndoChangeButton } from "./tools/UndoChangeButton";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { projectOpened, selectIsChatOpen } from "./slice";
import { Scene } from "./scene/Scene";
import { ChangeViewButton } from "./tools/ChangeViewButton";
import { SelectToolButton } from "./tools/SelectToolButton";
import { MenuButton } from "./tools/MenuButton";
import { NameInput } from "./tools/NameInput";
import { ChatButton } from "./tools/ChatButton";
import { Chat } from "../assistant/Chat";
import { AccountAvatar } from "../account/components";
import { PlanSelect } from "./tools/PlanSelect";
import { selectMyAccount } from "../account/slice";
import { AnimatePresence } from "motion/react";
import { Spinner } from "../../shared/components";

function ChatHelper({ projectId }: { projectId: string }) {
  const isChatOpen = useAppSelector(selectIsChatOpen);
  return (
    <AnimatePresence>
      {isChatOpen && <Chat projectId={projectId} />}
    </AnimatePresence>
  );
}

function ProjectEditorHelper({
  projectId,
  accountId,
  projectOwned,
}: {
  projectId: string;
  accountId: string;
  projectOwned: boolean;
}) {
  return (
    <>
      <div className="project-editor__menu">
        <MenuButton projectId={projectId} projectOwned={projectOwned} />
        <NameInput projectOwned={projectOwned} />
        <PlanSelect projectId={projectId} projectOwned={projectOwned} />
        <span />
        <AccountAvatar accountId={accountId} small />
        {projectOwned && (
          <>
            <span />
            <SelectToolButton
              tooltip={
                <p style={{ fontWeight: 400 }}>
                  This is <b>hand</b> tool. Use it to move around the scene.
                </p>
              }
              icon="hand.png"
              tool="hand"
            />
            <SelectToolButton
              tooltip={
                <p style={{ fontWeight: 400 }}>
                  This is <b>wall</b> tool. Use it to add walls. Start by
                  clicking at any point on the floor. Hold to draw a linear
                  wall.
                </p>
              }
              icon="wall.png"
              tool="wall"
            />
            <SelectToolButton
              tooltip={
                <p style={{ fontWeight: 400 }}>
                  This is <b>window</b> tool. Use it to add windows. Start by
                  clicking at any point on a wall. Hold to draw a
                  rectangular-shaped window.
                </p>
              }
              icon="window.png"
              tool="window"
            />
            <SelectToolButton
              tooltip={
                <p style={{ fontWeight: 400 }}>
                  This is <b>door</b> tool. Use it to add doors. Start by
                  clicking at any point on a wall. Hold to draw a
                  rectangular-shaped door.
                </p>
              }
              icon="door.png"
              tool="door"
            />
            <SelectToolButton
              tooltip={
                <p style={{ fontWeight: 400 }}>
                  This is <b>wet area</b> tool. Use it to draw wet areas. Start
                  by clicking at any point on the floor. Continue adding points
                  to draw a polygon-shaped wet area. Click the starting point
                  again to finish drawing.
                </p>
              }
              icon="raindrops.png"
              tool="wet_area"
            />
          </>
        )}
        <span />
        <ChangeViewButton />
        {projectOwned && (
          <>
            <span />
            <UndoChangeButton />
            <RedoChangeButton />
            <span />
            <ChatButton />
          </>
        )}
      </div>
      <ChatHelper projectId={projectId} />
      <Scene />
    </>
  );
}

export function ProjectEditor({ projectId }: { projectId: string }) {
  const { data: project, error, isLoading } = useGetProjectByIdQuery(projectId);
  const dispatch = useAppDispatch();
  const account = useAppSelector(selectMyAccount);

  useEffect(() => {
    if (project) {
      dispatch(projectOpened(project));
    }
  }, [project?.id]);

  if (isLoading) {
    return (
      <div className="project-editor__message">
        <Spinner />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="project-editor__message">
        <p>
          Can't load the project or the project does not exist.
          <br />
          Plese, try refreshing the page
        </p>
      </div>
    );
  }

  const projectOwned = Boolean(account && account.id === project.accountId);

  return (
    <ProjectEditorHelper
      projectId={projectId}
      projectOwned={projectOwned}
      accountId={project.accountId}
    />
  );
}
