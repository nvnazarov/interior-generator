import { useEffect } from "react";

import "./PlanEditor.scss";
import { useGetPlanByIdQuery, useGetProjectByIdQuery } from "../api/slice";
import { RedoChangeButton } from "./tools/RedoChangeButton";
import { UndoChangeButton } from "./tools/UndoChangeButton";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { selectIsChatOpen, planOpened, selectIsCatalogOpen } from "./slice";
import { Scene } from "./scene/Scene";
import { ChangeViewButton } from "./tools/ChangeViewButton";
import { SelectToolButton } from "./tools/SelectToolButton";
import { MenuButton } from "./tools/MenuButton";
import { NameInput } from "./tools/NameInput";
import { ChatButton } from "./tools/ChatButton";
import { Chat } from "../assistant/Chat";
import { Button } from "../../shared/components/button/Button";
import { AccountAvatar } from "../account/components";
import { PlanSelect } from "./tools/PlanSelect";
import { selectMyAccount } from "../account/slice";
import { AnimatePresence } from "motion/react";
import { FurnitureCatalogSwitch } from "./tools/FurnitureCatalogSwitch";
import { FurnitureCatalog } from "./tools/FurnitureCatalog";

function ChatHelper({ projectId }: { projectId: string }) {
  const isChatOpen = useAppSelector(selectIsChatOpen);
  return (
    <AnimatePresence>
      {isChatOpen && <Chat projectId={projectId} />}
    </AnimatePresence>
  );
}

function CatalogHelper() {
  const isCatalogOpen = useAppSelector(selectIsCatalogOpen);
  return (
    <AnimatePresence>{isCatalogOpen && <FurnitureCatalog />}</AnimatePresence>
  );
}

function PlanEditorHelper({
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
        <MenuButton projectId={projectId} />
        <NameInput />
        <PlanSelect projectId={projectId} />
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
                  This is <b>furniture</b> tool. Use it to modify furniture.
                </p>
              }
              icon="move.png"
              tool="furniture"
            />
            <SelectToolButton
              tooltip={
                <p style={{ fontWeight: 400 }}>
                  This is <b>functional area</b> tool. Use it to draw functional
                  areas. Start by clicking at any point on the floor. Continue
                  adding points to draw a polygon-shaped functional area. Click
                  the starting point again to finish drawing.
                </p>
              }
              icon="area.png"
              tool="area"
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
            <FurnitureCatalogSwitch />
            <ChatButton />
          </>
        )}
      </div>
      <ChatHelper projectId={projectId} />
      <CatalogHelper />
      <Scene />
    </>
  );
}

export function PlanEditor({
  planId,
  projectId,
}: {
  planId: string;
  projectId: string;
}) {
  const {
    data: plan,
    error: planLoadingError,
    isLoading: isPlanLoading,
  } = useGetPlanByIdQuery(planId);
  const {
    data: project,
    error: projectLoadingError,
    isLoading: isProjectLoading,
  } = useGetProjectByIdQuery(projectId);
  const dispatch = useAppDispatch();
  const account = useAppSelector(selectMyAccount);

  useEffect(() => {
    if (plan) {
      dispatch(planOpened(plan));
    }
  }, [plan]);

  if (isPlanLoading || isProjectLoading) {
    return <>Loading</>;
  }

  if (planLoadingError || projectLoadingError || !plan || !project) {
    return (
      <>
        <Button text="Refresh" />
      </>
    );
  }

  const projectOwned = Boolean(account && account.id === project.accountId);

  return (
    <PlanEditorHelper
      projectId={projectId}
      projectOwned={projectOwned}
      accountId={project.accountId}
    />
  );
}
