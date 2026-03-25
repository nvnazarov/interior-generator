import { createSlice } from "@reduxjs/toolkit";
import type { ProjectPatch } from "../../../features/project/project";
import type { ProjectChange } from "../../../features/project/editor";

type ProjectEditorState = {
  projectId: string;
  unsyncedAccumulatedPatch: ProjectPatch;
  undoableChanges: ProjectChange[];
  redoableChanges: ProjectChange[];
  view: "2D" | "3D";
  tool: "hand" | "wall" | "window" | "door" | "wet_area";
};

type PlanEditorState = {
  planId: string;
  unsyncedAccumulatedPatch: ProjectPatch;
  undoableChanges: ProjectChange[];
  redoableChanges: ProjectChange[];
  view: "2D" | "3D";
  tool: "hand" | "area";
};

type EditorState = { project: ProjectEditorState } | { plan: PlanEditorState };

const editorSlice = createSlice({
  name: "editor",
  initialState: {} as EditorState,
  reducers: {},
});

export default editorSlice.reducer;
export type { EditorState };
