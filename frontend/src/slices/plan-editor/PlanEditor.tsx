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
import { AccountAvatar } from "../account/components";
import { PlanSelect } from "./tools/PlanSelect";
import { selectMyAccount } from "../account/slice";
import { FurnitureCatalogSwitch } from "./tools/FurnitureCatalogSwitch";
import { FurnitureCatalog } from "./tools/FurnitureCatalog";
import { Spinner } from "../../shared/components";

function ChatHelper({ projectId }: { projectId: string }) {
  const isChatOpen = useAppSelector(selectIsChatOpen);
  return <>{isChatOpen && <Chat projectId={projectId} />}</>;
}

function CatalogHelper() {
  const isCatalogOpen = useAppSelector(selectIsCatalogOpen);
  return <>{isCatalogOpen && <FurnitureCatalog />}</>;
}

function PlanEditorHelper({
  planId,
  projectId,
  accountId,
  projectOwned,
}: {
  planId: string;
  projectId: string;
  accountId: string;
  projectOwned: boolean;
}) {
  return (
    <>
      <div className="plan-editor__menu">
        <MenuButton
          projectId={projectId}
          planId={planId}
          projectOwned={projectOwned}
        />
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
  }, [plan?.id]);

  if (isPlanLoading || isProjectLoading) {
    return (
      <div className="plan-editor__message">
        <Spinner />
      </div>
    );
  }

  if (planLoadingError || projectLoadingError || !plan || !project) {
    return (
      <div className="plan-editor__message">
        <p>
          Can't load the plan or the plan does not exist.
          <br />
          Plese, try refreshing the page
        </p>
      </div>
    );
  }

  const projectOwned = Boolean(account && account.id === project.accountId);

  return (
    <PlanEditorHelper
      planId={planId}
      projectId={projectId}
      projectOwned={projectOwned}
      accountId={project.accountId}
    />
  );
}
