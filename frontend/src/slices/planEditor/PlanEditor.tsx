import "./PlanEditor.scss";
import { useEffect } from "react";
import { useLazyGetPlanByIdQuery } from "../api/slice";
import { RedoChangeButton } from "./RedoChangeButton";
import { SaveButton } from "./SaveButton";
import { UndoChangeButton } from "./UndoChangeButton";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { planOpened, selectIsCatalogOpen, selectIsChatOpen } from "./slice";
import { Button, ContextMenuProvider } from "../../shared/components";
import { Scene } from "./Scene";
import { ChangeViewButton } from "./ChangeViewButton";
import { SelectToolButton } from "./SelectToolButton";
import { MenuButton } from "./MenuButton";
import { FurnitureCatalog } from "./FurnitureCatalog";
import { FurnitureCatalogSwitch } from "./FurnitureCatalogSwitch";
import { NameInput } from "./NameInput";
import { Hint } from "./Hint";
import { ChatButton } from "./ChatButton";
import { Chat } from "../prompts/Chat";

export function PlanEditor({
  projectId,
  planId,
}: {
  projectId: string;
  planId: string;
}) {
  const [getPlanById, { error }] = useLazyGetPlanByIdQuery();
  const dispatch = useAppDispatch();
  const isCatalogOpen = useAppSelector(selectIsCatalogOpen);
  const isChatOpen = useAppSelector(selectIsChatOpen);

  useEffect(() => {
    async function loadPlan() {
      const plan = await getPlanById(planId).unwrap();
      dispatch(planOpened(plan));
    }
    loadPlan();
  }, [planId]);

  if (error) {
    return (
      <>
        <Button title="Refresh" />
      </>
    );
  }

  return (
    <ContextMenuProvider>
      <div className="plan-editor__plan-editor__menu">
        <div>
          <MenuButton planId={planId} projectId={projectId} />
        </div>
        <span />
        <div>
          <NameInput />
        </div>
        <div>
          <SelectToolButton icon="hand.png" tool="hand" />
          <SelectToolButton icon="area.png" tool="area" />
          <SelectToolButton icon="move.png" tool="furniture" />
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
          <FurnitureCatalogSwitch />
        </div>
      </div>
      {isCatalogOpen && <FurnitureCatalog />}
      {isChatOpen && <Chat projectId={projectId} />}
      <Scene />
      <Hint />
    </ContextMenuProvider>
  );
}
