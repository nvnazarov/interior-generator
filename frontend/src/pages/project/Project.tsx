import "./Project.scss";
import { useParams } from "react-router";
import { ProjectEditor } from "../../features/project/components/ProjectEditor";
import { ProjectInfo } from "../../features/project/components/ProjectInfo";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {
  fetchProject,
  selectProjectById,
  selectProjectEditor,
} from "../../features/project/slice";
import { FurnitureCatalog } from "../../features/furniture";
import {
  RedoButton,
  ToolsContainer,
  ToolSelector,
  UndoButton,
  ViewModeSwitch,
} from "../../features/project";
import { EditorSelector } from "../../features/project/components/EditorSelector";
import { AddPlanButton } from "../../features/plan/components/AddPlanButton";
import { useEffect } from "react";

export function Project() {
  const dispatch = useAppDispatch();
  const { id } = useParams();
  if (!id) {
    throw new Error("bug");
  }
  const project = useAppSelector(selectProjectById(id));
  const editor = useAppSelector(selectProjectEditor);

  useEffect(() => {
    if (!project) {
      // TODO: handle errors
      dispatch(fetchProject(id));
    }
  }, [project]);

  if (!project) {
    return <div className="page__project">Loading</div>;
  }

  return (
    <div className="page__project">
      <div className="page__project__toolbar">
        <ToolsContainer>
          <ProjectInfo projectId={id} />
          <EditorSelector projectId={id} />
          <AddPlanButton projectId={id} />
        </ToolsContainer>
        <ToolsContainer>
          <ViewModeSwitch />
        </ToolsContainer>
        <ToolsContainer>
          <ToolSelector tool="hand" icon="icons/hand.png" />
          <ToolSelector tool="window" icon="icons/window.png" />
          <ToolSelector tool="door" icon="icons/door.png" />
          <ToolSelector tool="wall" icon="icons/wall.png" />
        </ToolsContainer>
        <ToolsContainer>
          <UndoButton />
          <RedoButton />
        </ToolsContainer>
      </div>
      <div className="page__project__editor">
        <ProjectEditor id={id} />
      </div>
      {editor.isCatalogOpen && (
        <div className="page__project__catalog">
          <FurnitureCatalog />
        </div>
      )}
    </div>
  );
}
