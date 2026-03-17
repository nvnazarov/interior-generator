import "./Project.scss";
import { useParams } from "react-router";
import { ProjectEditor } from "../../features/project/components/ProjectEditor";
import { ProjectInfo } from "../../features/project/components/ProjectInfo";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {
  fetchProject,
  selectProjectById,
  selectProjectEditorProject,
  setEditorProject,
  syncProjectEditorChanges,
} from "../../features/project/slice";
import {
  RedoButton,
  SyncButton,
  ToolsContainer,
  ToolSelector,
  UndoButton,
  ViewModeSwitch,
} from "../../features/project";
import { EditorSelector } from "../../features/project/components/EditorSelector";
import { AddPlanButton } from "../../features/plan/components/AddPlanButton";
import { useEffect } from "react";
import { SyncAge } from "../../features/project/components/SyncAge";
import { fetchAllPlansInProject } from "../../features/plan/thunks";

export function Project() {
  const dispatch = useAppDispatch();
  const { projectId } = useParams();
  if (!projectId) {
    throw new Error("bug");
  }
  const project = useAppSelector(selectProjectById(projectId));

  useEffect(() => {
    if (!project || project.etag === "") {
      // TODO: handle errors
      dispatch(fetchProject(projectId));
      dispatch(fetchAllPlansInProject(projectId));
      return;
    }
    dispatch(setEditorProject(project));
    const intervalId = setInterval(() => {
      dispatch(syncProjectEditorChanges());
    }, 10000);
    return () => {
      clearInterval(intervalId);
    };
  }, [project]);

  if (!project) {
    return <div className="page__project">Loading</div>;
  }

  return (
    <div className="page__project">
      <div className="page__project__toolbar">
        <ToolsContainer>
          <ProjectInfo />
          <EditorSelector projectId={projectId} />
          <AddPlanButton projectId={projectId} />
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
        <ToolsContainer>
          <SyncAge />
          <SyncButton />
        </ToolsContainer>
      </div>
      <div className="page__project__editor">
        <ProjectEditor />
      </div>
    </div>
  );
}
