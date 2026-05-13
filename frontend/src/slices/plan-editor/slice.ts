import {
  createSlice,
  current,
  original,
  type PayloadAction,
} from "@reduxjs/toolkit";
import type { FurnitureInPlan, Plan, PlanPatch } from "../api/entities";
import {
  applyJsonMergePatch,
  combineJsonMergePatches,
  computeJsonMergePatch,
} from "../../shared/lib/jsonMergePatch";
import type { AppState } from "../store";

type View = "2D" | "3D";

type Tool = "hand" | "furniture" | "area";

type PlanChange = {
  patch: PlanPatch;
  inversePatch: PlanPatch;
};

type FurnitureDrag = {
  furnitureId: string;
  furnitureInPlan: FurnitureInPlan & { id: string };
};

export type PlanEditorState = {
  plan: Plan | null;
  unsavedAccumulatedPatch: PlanPatch;
  undoableChanges: PlanChange[];
  redoableChanges: PlanChange[];
  view: View;
  tool: Tool;
  isCatalogOpen: boolean;
  isChatOpen: boolean;
  furnitureDrag: FurnitureDrag | null;
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
    isCatalogOpen: false,
    isChatOpen: false,
    furnitureDrag: null,
  } as PlanEditorState,
  reducers: {
    planOpened: (state, action: PayloadAction<Plan>) => {
      state.plan = action.payload;
      state.unsavedAccumulatedPatch = {};
      state.undoableChanges = [];
      state.redoableChanges = [];
      state.view = "2D";
      state.tool = "hand";
      state.isCatalogOpen = false;
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
    planUndoablyChanged: (state, action: PayloadAction<PlanPatch>) => {
      const patch = action.payload;
      if (state.plan) {
        state.plan = applyJsonMergePatch(state.plan, patch);
      } else {
        throw new Error(
          "error: plan undoably changed: plan is not initialized",
        );
      }
      state.unsavedAccumulatedPatch = combineJsonMergePatches(
        state.unsavedAccumulatedPatch,
        patch,
      );
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
    planChangedTo: (state, action: PayloadAction<Plan["content"]>) => {
      if (state.plan) {
        const oldContent =
          original(state.plan.content) ?? current(state.plan.content);
        const patch = computeJsonMergePatch(oldContent, action.payload);
        if (!patch || Object.keys(patch).length === 0) {
          return;
        }
        const newContent = applyJsonMergePatch(oldContent, patch);
        state.plan.content = newContent;
        const inversePatch = computeJsonMergePatch(newContent, oldContent);
        const change = {
          patch: { content: patch },
          inversePatch: { content: inversePatch },
        } as PlanChange;
        state.unsavedAccumulatedPatch = combineJsonMergePatches(
          state.unsavedAccumulatedPatch,
          change.patch,
        );
        state.undoableChanges.push(change);
        state.redoableChanges = [];
      }
    },
    changeUndone: (state) => {
      const change = state.undoableChanges.pop();
      if (!change) {
        throw new Error("error: change undone: no undoable changes");
      }
      if (state.plan) {
        const oldPlan = current(state.plan);
        const patch = current(change.inversePatch);
        const newPlan = applyJsonMergePatch(oldPlan, patch);
        state.plan = newPlan;
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
    planSaved: (state, action: PayloadAction<number>) => {
      if (state.plan) {
        state.plan.revision = action.payload;
      } else {
        throw new Error("error: plan saved: plan is not initialized");
      }
      state.unsavedAccumulatedPatch = {};
    },
    catalogSwitched: (state) => {
      state.isCatalogOpen = !state.isCatalogOpen;
      if (state.isCatalogOpen) {
        state.isChatOpen = false;
      }
    },
    chatSwitched: (state) => {
      state.isChatOpen = !state.isChatOpen;
      if (state.isChatOpen) {
        state.isCatalogOpen = false;
      }
    },
    startedDraggingFurniture: (state, action: PayloadAction<FurnitureDrag>) => {
      state.furnitureDrag = action.payload;
    },
    finishedDraggingFurniture: (state) => {
      state.furnitureDrag = null;
    },
  },
});

export const selectPlanEditor = (state: AppState) => state.planEditor;
export const selectCanUndoChange = (state: AppState) =>
  state.planEditor.undoableChanges.length !== 0;
export const selectCanRedoChange = (state: AppState) =>
  state.planEditor.redoableChanges.length !== 0;
export const selectPlanEditorView = (state: AppState) => state.planEditor.view;
export const selectPlanEditorTool = (state: AppState) => state.planEditor.tool;
export const selectIsPlanSaved = (state: AppState) =>
  Object.keys(state.planEditor.unsavedAccumulatedPatch).length === 0;
export const selectPlan = (state: AppState) => state.planEditor.plan;
export const selectIsCatalogOpen = (state: AppState) =>
  state.planEditor.isCatalogOpen;
export const selectIsChatOpen = (state: AppState) =>
  state.planEditor.isChatOpen;
export const selectFurnitureDrag = (state: AppState) =>
  state.planEditor.furnitureDrag;

export default planEditorSlice.reducer;
export const {
  viewChanged,
  toolSelected,
  changeRedone,
  changeUndone,
  planSaved,
  planChanged,
  planChangedTo,
  planOpened,
  catalogSwitched,
  chatSwitched,
  startedDraggingFurniture,
  finishedDraggingFurniture,
  planUndoablyChanged,
} = planEditorSlice.actions;
