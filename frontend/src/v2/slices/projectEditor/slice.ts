import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { ProjectPatch } from "../../../features/project/project";
import type { ProjectChange } from "../../../features/project/editor";
import type { Project } from "../api/entities";
import {
  applyJsonMergePatch,
  combineJsonMergePatches,
} from "../../shared/lib/jsonMergePatch";
import type { AppState } from "../store";

type View = "2D" | "3D";

type Tool = "hand" | "wall" | "window" | "door" | "wet_area";

type ProjectEditorState = {
  project: Project | null;
  unsavedAccumulatedPatch: ProjectPatch;
  undoableChanges: ProjectChange[];
  redoableChanges: ProjectChange[];
  view: View;
  tool: Tool;
};

const projectEditorSlice = createSlice({
  name: "editor",
  initialState: {
    project: null,
    unsavedAccumulatedPatch: {},
    undoableChanges: [],
    redoableChanges: [],
    view: "2D",
    tool: "hand",
  } as ProjectEditorState,
  reducers: {
    projectOpened: (state, action: PayloadAction<Project>) => {
      state.project = action.payload;
      state.unsavedAccumulatedPatch = {};
      state.undoableChanges = [];
      state.redoableChanges = [];
      state.view = "2D";
      state.tool = "hand";
    },
    toolSelected: (state, action: PayloadAction<Tool>) => {
      const tool = action.payload;
      state.tool = tool;
      if (["wall", "wet_area"].includes(tool)) {
        state.view = "2D";
      }
      if (["window", "door"].includes(tool)) {
        state.view = "3D";
      }
    },
    viewChanged: (state, action: PayloadAction<View>) => {
      const view = action.payload;
      state.view = view;
      if (view === "2D" && ["door", "window"].includes(state.tool)) {
        state.tool = "hand";
      }
      if (view === "3D" && ["wall", "wet_area"].includes(state.tool)) {
        state.tool = "hand";
      }
    },
    projectChanged: (state, action: PayloadAction<ProjectChange>) => {
      const change = action.payload;
      if (state.project) {
        state.project = applyJsonMergePatch(state.project, change.patch);
      } else {
        throw new Error("error: project changed: project is not initialized");
      }
      state.unsavedAccumulatedPatch = combineJsonMergePatches(
        state.unsavedAccumulatedPatch,
        change.patch,
      );
      state.undoableChanges.push(change);
      state.redoableChanges = [];
    },
    changeUndone: (state) => {
      const change = state.undoableChanges.pop();
      if (!change) {
        throw new Error("error: change undone: no undoable changes");
      }
      if (state.project) {
        state.project = applyJsonMergePatch(state.project, change.inversePatch);
      } else {
        throw new Error("error: change undone: project is not initialized");
      }
      state.unsavedAccumulatedPatch = combineJsonMergePatches(
        state.unsavedAccumulatedPatch,
        change.inversePatch,
      );
      state.redoableChanges.push(change);
    },
    changeRedone: (state) => {
      const change = state.redoableChanges.pop();
      if (!change) {
        throw new Error("error: change redone: no redoable changes");
      }
      if (state.project) {
        state.project = applyJsonMergePatch(state.project, change.patch);
      } else {
        throw new Error("error: change redone: project is not initialized");
      }
      state.unsavedAccumulatedPatch = combineJsonMergePatches(
        state.unsavedAccumulatedPatch,
        change.patch,
      );
      state.undoableChanges.push(change);
    },
    projectSaved: (state, action: PayloadAction<string>) => {
      if (state.project) {
        state.project.revision = action.payload;
      } else {
        throw new Error("error: project saved: project is not initialized");
      }
      state.unsavedAccumulatedPatch = {};
    },
  },
});

export const selectProjectEditor = (state: AppState) => state.projectEditor;
export const selectCanUndoChange = (state: AppState) => state.projectEditor.undoableChanges.length !== 0;
export const selectCanRedoChange = (state: AppState) => state.projectEditor.redoableChanges.length !== 0;
export const selectProjectEditorView = (state: AppState) => state.projectEditor.view;
export const selectProjectEditorTool = (state: AppState) => state.projectEditor.tool;
export const selectIsProjectSaved = (state: AppState) => Object.keys(state.projectEditor.unsavedAccumulatedPatch).length === 0;
export const selectProject = (state: AppState) => state.projectEditor.project;

export default projectEditorSlice.reducer;
export const {
  viewChanged,
  toolSelected,
  changeRedone,
  changeUndone,
  projectSaved,
  projectChanged,
  projectOpened,
} = projectEditorSlice.actions;
