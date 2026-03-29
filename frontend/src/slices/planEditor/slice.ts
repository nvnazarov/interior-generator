import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Plan, PlanPatch } from "../api/entities";
import {
  applyJsonMergePatch,
  combineJsonMergePatches,
} from "../../shared/lib/jsonMergePatch";
import type { AppState } from "../store";

type View = "2D" | "3D";

type Tool = "hand" | "furniture" | "area";

type PlanChange = {
  patch: PlanPatch;
  inversePatch: PlanPatch;
}

type PlanEditorState = {
  plan: Plan | null;
  unsavedAccumulatedPatch: PlanPatch;
  undoableChanges: PlanChange[];
  redoableChanges: PlanChange[];
  view: View;
  tool: Tool;
};

const planEditorSlice = createSlice({
  name: "planEditor",
  initialState: {
    plan: null,
    unsavedAccumulatedPatch: {},
    undoableChanges: [],
    redoableChanges: [],
    view: "2D",
    tool: "hand",
  } as PlanEditorState,
  reducers: {
    planOpened: (state, action: PayloadAction<Plan>) => {
      state.plan = action.payload;
      state.unsavedAccumulatedPatch = {};
      state.undoableChanges = [];
      state.redoableChanges = [];
      state.view = "2D";
      state.tool = "hand";
    },
    toolSelected: (state, action: PayloadAction<Tool>) => {
      const tool = action.payload;
      state.tool = tool;
      if (tool === "area") {
        state.view = "2D";
      }
      if (tool === "furniture") {
        state.view = "3D";
      }
    },
    viewChanged: (state, action: PayloadAction<View>) => {
      const view = action.payload;
      state.view = view;
      if (view === "2D" && state.tool === "furniture") {
        state.tool = "hand";
      }
      if (view === "3D" && state.tool === "area") {
        state.tool = "hand";
      }
    },
    planChanged: (state, action: PayloadAction<PlanChange>) => {
      const change = action.payload;
      if (state.plan) {
        state.plan = applyJsonMergePatch(state.plan, change.patch);
      } else {
        throw new Error("error: plan changed: plan is not initialized");
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
      if (state.plan) {
        state.plan = applyJsonMergePatch(state.plan, change.inversePatch);
      } else {
        throw new Error("error: change undone: plan is not initialized");
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
      if (state.plan) {
        state.plan = applyJsonMergePatch(state.plan, change.patch);
      } else {
        throw new Error("error: change redone: plan is not initialized");
      }
      state.unsavedAccumulatedPatch = combineJsonMergePatches(
        state.unsavedAccumulatedPatch,
        change.patch,
      );
      state.undoableChanges.push(change);
    },
    planSaved: (state, action: PayloadAction<string>) => {
      if (state.plan) {
        state.plan.revision = action.payload;
      } else {
        throw new Error("error: plan saved: plan is not initialized");
      }
      state.unsavedAccumulatedPatch = {};
    },
  },
});

export const selectPlanEditor = (state: AppState) => state.planEditor;
export const selectCanUndoChange = (state: AppState) => state.planEditor.undoableChanges.length !== 0;
export const selectCanRedoChange = (state: AppState) => state.planEditor.redoableChanges.length !== 0;
export const selectPlanEditorView = (state: AppState) => state.planEditor.view;
export const selectPlanEditorTool = (state: AppState) => state.planEditor.tool;
export const selectIsPlanSaved = (state: AppState) => Object.keys(state.planEditor.unsavedAccumulatedPatch).length === 0;
export const selectPlan = (state: AppState) => state.planEditor.plan;

export default planEditorSlice.reducer;
export const {
  viewChanged,
  toolSelected,
  changeRedone,
  changeUndone,
  planSaved,
  planChanged,
  planOpened,
} = planEditorSlice.actions;
