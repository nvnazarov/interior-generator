import {
  createAsyncThunk,
  createEntityAdapter,
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";
import type { ProjectEditor } from "./editor";
import { Client } from "../../shared/client";
import type { Project, ProjectPatch } from "./project";

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

export const patchProject = createAsyncThunk(
  "projects/patchProject",
  async ({
    projectId,
    patch,
    etag,
  }: {
    projectId: string;
    patch: ProjectPatch;
    etag: string;
  }) => {
    const newEtag = await Client.projects.patch(projectId, patch, etag);
    return newEtag;
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
    optimisticPatchProject: (state, action: PayloadAction<{ id: string, patch: ProjectPatch }>) => {
      const payload = action.payload;
      projectAdapter.updateOne(state, {
        id: payload.id,
        changes: payload.patch,
      });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAllOwnedProjects.pending, () => { })
      .addCase(fetchAllOwnedProjects.fulfilled, (state, action) => {
        projectAdapter.setAll(state, action.payload);
      })
      .addCase(fetchAllOwnedProjects.rejected, () => { })
      .addCase(createProject.pending, () => { })
      .addCase(createProject.fulfilled, (state, action) => {
        projectAdapter.addOne(state, action.payload);
      })
      .addCase(createProject.rejected, () => { })
      .addCase(deleteProject.pending, () => { })
      .addCase(deleteProject.fulfilled, (state, action) => {
        projectAdapter.removeOne(state, action.meta.arg);
      })
      .addCase(deleteProject.rejected, () => { })
      .addCase(publishProject.pending, () => { })
      .addCase(publishProject.fulfilled, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.meta.arg,
          changes: { published: true },
        });
      })
      .addCase(publishProject.rejected, () => { })
      .addCase(unpublishProject.pending, () => { })
      .addCase(unpublishProject.fulfilled, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.meta.arg,
          changes: { published: false },
        });
      })
      .addCase(unpublishProject.rejected, () => { })
      // .addCase(fetchProject.pending, (state, action) => {
      //   projectAdapter.updateOne(state, {
      //     id: action.meta.arg,
      //     changes: { status: "pending" },
      //   });
      // })
      // .addCase(fetchProject.rejected, (state, action) => {
      //   projectAdapter.updateOne(state, {
      //     id: action.meta.arg,
      //     changes: { status: "failure" },
      //   });
      // })
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
    zoom: 1,
    undo: [],
    redo: [],
    activeTool: "hand",
    isDirty: false,
    isCatalogOpen: false,
    dtLastSaved: null,
  } as ProjectEditor,
  reducers: {
    openCatalog(state) {
      state.isCatalogOpen = true;
    },
    closeCatalog(state) {
      state.isCatalogOpen = false;
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
    undo(state) { },
    redo(state) { },
  },
});

export const { optimisticPatchProject } = projectSlice.actions;
export const {
  openCatalog,
  closeCatalog,
  switchViewMode,
  selectTool,
  undo,
  redo,
} = projectEditorSlice.actions;
export const selectProjectEditor = (state: RootState) => state.projectEditor;
export const selectActiveTool = (state: RootState) =>
  state.projectEditor.activeTool;
export const selectCanUndo = (state: RootState) =>
  state.projectEditor.undo.length !== 0;
export const selectCanRedo = (state: RootState) =>
  state.projectEditor.redo.length !== 0;

export const projectEditorReducer = projectEditorSlice.reducer;
export const projectsReducer = projectSlice.reducer;
