import {
  createAsyncThunk,
  createEntityAdapter,
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";
import type { ProjectChange, ProjectEditor } from "./editor";
import { Client } from "../../shared/client";
import { ProjectUtils, type Project, type ProjectPatch } from "./project";
import { createAppAsyncThunk } from "../../app/withTypes";
import moment from "moment";

export const fetchAllOwnedProjects = createAsyncThunk(
  "projects/fetchAllOwnedProjects",
  Client.projects.getAllOwned,
);

export const fetchProject = createAsyncThunk(
  "projects/fetchProjectById",
  Client.projects.getById,
);

export const createProject = createAsyncThunk(
  "projects/createProject",
  Client.projects.create,
);

export const deleteProject = createAsyncThunk(
  "projects/deleteProject",
  Client.projects.delete,
);

export const publishProject = createAsyncThunk(
  "projects/publishProject",
  Client.projects.publish,
);

export const unpublishProject = createAsyncThunk(
  "projects/unpublishProject",
  Client.projects.unpublish,
);

export const exportProjectPDF = createAsyncThunk(
  "projects/exportProjectPDF",
  async (projectId: string) => {
    const blob = await Client.exporter.exportProjectPDF(projectId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `project-${projectId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    return projectId;
  },
);

const projectAdapter = createEntityAdapter<Project, string>({
  selectId: (project) => project.id,
  sortComparer: (a, b) => a.dtUpdated.localeCompare(b.dtUpdated),
});

const projectSlice = createSlice({
  name: "projects",
  initialState: projectAdapter.getInitialState(),
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAllOwnedProjects.fulfilled, (state, action) => {
        projectAdapter.setAll(state, action.payload);
      })
      .addCase(createProject.fulfilled, (state, action) => {
        projectAdapter.addOne(state, action.payload);
      })
      .addCase(deleteProject.fulfilled, (state, action) => {
        projectAdapter.removeOne(state, action.meta.arg);
      })
      .addCase(publishProject.fulfilled, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.meta.arg,
          changes: { published: true },
        });
      })
      .addCase(unpublishProject.fulfilled, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.meta.arg,
          changes: { published: false },
        });
      })
      .addCase(unpublishProject.rejected, () => { })
      .addCase(fetchProject.fulfilled, (state, action) => {
        projectAdapter.setOne(state, action.payload);
      });
  },
});

const selectors = projectAdapter.getSelectors<RootState>(
  (state) => state.projects,
);

export const selectAllProjects = selectors.selectAll;
export const selectProjectById = (id: string) => (state: RootState) =>
  selectors.selectById(state, id);
export const selectTotalProjects = selectors.selectTotal;

const projectEditorSlice = createSlice({
  name: "projectEditor",
  initialState: {
    viewMode: "2d",
    undo: [],
    redo: [],
    sync: [],
    activeTool: "hand",
    dtLastSaved: moment().toISOString(),
    project: null,
  } as ProjectEditor,
  reducers: {
    savedNow(state) {
      state.dtLastSaved = moment().toISOString();
    },
    setEditorProject(state, action: PayloadAction<Project>) {
      state.project = action.payload;
    },
    setEditorProjectEtag(state, action: PayloadAction<string>) {
      if (!state.project) {
        throw new Error("BUG")
      }
      state.project.etag = action.payload;
    },
    switchViewMode(state) {
      state.viewMode = state.viewMode === "2d" ? "3d" : "2d";
    },
    selectTool(
      state,
      action: PayloadAction<"hand" | "wall" | "window" | "door">,
    ) {
      state.activeTool = action.payload;
    },
    setSync(state, action: PayloadAction<ProjectPatch[]>) {
      state.sync = action.payload;
    },
    undo(state) {
      const project = state.project;
      if (!project) {
        throw new Error("BUG");
      }
      const change = state.undo.pop()
      if (!change) {
        throw new Error("BUG")
      }
      state.project = ProjectUtils.applyPatch(project, change.inversePatch)
      state.redo.push(change);
      state.sync.push(change.inversePatch);
    },
    redo(state) {
      const project = state.project;
      if (!project) {
        throw new Error("BUG");
      }
      const change = state.redo.pop()
      if (!change) {
        throw new Error("BUG")
      }
      state.project = ProjectUtils.applyPatch(project, change.patch)
      state.undo.push(change);
      state.sync.push(change.patch);
    },
    recordProjectChange: (state, action: PayloadAction<ProjectChange>) => {
      const project = state.project;
      if (!project) {
        throw new Error("BUG");
      }
      const change = action.payload;
      state.project = ProjectUtils.applyPatch(project, change.patch)
      state.undo.push(change)
      state.sync.push(change.patch)
      state.redo = [];
    },
  },
});

export const {
  recordProjectChange, setEditorProject,
  switchViewMode,
  selectTool,
  undo,
  redo,
  setSync,
  setEditorProjectEtag,
  savedNow,
} = projectEditorSlice.actions;
export const selectProjectEditor = (state: RootState) => state.projectEditor;
export const selectProjectEditorProject = (state: RootState) => state.projectEditor.project;
export const selectActiveTool = (state: RootState) =>
  state.projectEditor.activeTool;
export const selectCanUndo = (state: RootState) =>
  state.projectEditor.undo.length !== 0;
export const selectCanRedo = (state: RootState) =>
  state.projectEditor.redo.length !== 0;
export const selectCanSync = (state: RootState) => state.projectEditor.sync.length !== 0

export const projectEditorReducer = projectEditorSlice.reducer;
export const projectsReducer = projectSlice.reducer;

export const syncProjectEditorChanges = createAppAsyncThunk(
  "projectEditor/syncChanges",
  async (_, api) => {
    const state = api.getState()
    const project = state.projectEditor.project;
    if (!project) {
      throw new Error("BUG");
    }
    const oldSync = [...state.projectEditor.sync];
    const patch = ProjectUtils.mergePatches(state.projectEditor.sync);
    api.dispatch(setSync([]));
    if (Object.keys(patch).length === 0) {
      return;
    }
    try {
      const newEtag = await Client.projects.patch(project.id, patch, project.etag);
      api.dispatch(setEditorProjectEtag(newEtag))
      api.dispatch(savedNow())
    } catch {
      api.dispatch(setSync([...oldSync, ...state.projectEditor.sync]));
    }
  },
);