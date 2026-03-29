import "./PlanEditor.scss";
import { useEffect } from "react";
import { useLazyGetPlanByIdQuery } from "../api/slice";
import { RedoChangeButton } from "./RedoChangeButton";
import { SaveButton } from "./SaveButton";
import { UndoChangeButton } from "./UndoChangeButton";
import { useAppDispatch } from "../storeTypes";
import { planOpened } from "./slice";
import { Button, ContextMenuProvider } from "../../shared/components";
import { Scene } from "./Scene";
import { ChangeViewButton } from "./ChangeViewButton";
import { SelectToolButton } from "./SelectToolButton";
import { MenuButton } from "./MenuButton";

export function PlanEditor({
  projectId,
  planId,
}: {
  projectId: string;
  planId: string;
}) {
  const [getPlanById, { error }] = useLazyGetPlanByIdQuery();
  const dispatch = useAppDispatch();

  useEffect(() => {
    async function loadProject() {
      const project = await getPlanById(planId).unwrap();
      dispatch(planOpened(project));
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
      <div className="plan-editor__plan-editor__menu">
        <div>
          <MenuButton planId={planId} projectId={projectId} />
        </div>
        <span />
        <div>
          <SelectToolButton icon="hand.png" tool="hand" />
          <SelectToolButton icon="area.png" tool="area" />
          <SelectToolButton icon="furniture.png" tool="furniture" />
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
