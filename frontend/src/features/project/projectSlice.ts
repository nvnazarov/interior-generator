import {
  createAsyncThunk,
  createEntityAdapter,
  createSlice,
} from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";
import { CONFIG } from "../../shared/config";

export const MAX_PROJECTS_COUNT = 20;
export const MAX_PROJECT_NAME_LENGTH = 256;
export const MAX_PROJECT_DESCRIPTION_LENGTH = 2048;

export interface Content {
  walls: any[];
  windows: any[];
  doors: any[];
  wet_areas: any[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  published: boolean;
  created_at: string;
  updated_at: string;
  content: Content;
  status: "pending" | "success" | "failure";
}

export const fetchProjects = createAsyncThunk(
  "projects/fetchProjects",
  async () => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/projects`);
    if (!resp.ok) {
      throw new Error("failed to fetch projects");
    }
    const data = (await resp.json()) as Project[];
    return data;
  },
);

export const fetchProject = createAsyncThunk(
  "projects/fetchProject",
  async (id: string) => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/projects/${id}`);
    if (!resp.ok) {
      throw new Error("failed to fetch the project");
    }
    const data = (await resp.json()) as Project;
    return data;
  },
);

export const createProject = createAsyncThunk(
  "projects/createProject",
  async () => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/projects`, {
      method: "POST",
    });
    if (!resp.ok) {
      throw new Error("failed to create project");
    }
    const data = (await resp.json()) as Project;
    return data;
  },
);

export const deleteProject = createAsyncThunk(
  "projects/deleteProject",
  async (id: string) => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/projects/${id}`, {
      method: "DELETE",
    });
    if (!resp.ok) {
      throw new Error("failed to delete the project");
    }
    return id;
  },
);

export const publishProject = createAsyncThunk(
  "projects/publishProject",
  async (id: string) => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${id}/publish`,
      { method: "POST" },
    );
    if (!resp.ok) {
      throw new Error("failed to publish the project");
    }
    return id;
  },
);

export const unpublishProject = createAsyncThunk(
  "projects/unpublishProject",
  async (id: string) => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${id}/unpublish`,
      { method: "POST" },
    );
    if (!resp.ok) {
      throw new Error("failed to unpublish the project");
    }
    return id;
  },
);

export const exportProjectPDF = createAsyncThunk(
  "projects/exportProjectPDF",
  async (id: string) => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${id}/export/pdf`,
      {
        method: "POST",
        body: "{}",
        headers: { "Content-Type": "application/json" },
      },
    );
    if (!resp.ok) {
      throw new Error("failed to export the project");
    }
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `project-${id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    return id;
  },
);

export const patchProject = createAsyncThunk(
  "projects/patchProject",
  async (id: string) => { },
);

const projectAdapter = createEntityAdapter<Project, string>({
  selectId: (project) => project.id,
  sortComparer: (a, b) => a.updated_at.localeCompare(b.updated_at),
});

const projectSlice = createSlice({
  name: "projects",
  initialState: projectAdapter.getInitialState(),
  reducers: {
    optimisticPatchProject: (state, action) => {
      const patch = action.payload;
      projectAdapter.updateOne(state, {
        id: patch.id,
        changes: patch,
      });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProjects.pending, () => { })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        projectAdapter.setAll(state, action.payload);
      })
      .addCase(fetchProjects.rejected, () => { })
      .addCase(createProject.pending, () => { })
      .addCase(createProject.fulfilled, (state, action) => {
        projectAdapter.addOne(state, action.payload);
      })
      .addCase(createProject.rejected, () => { })
      .addCase(deleteProject.pending, () => { })
      .addCase(deleteProject.fulfilled, (state, action) => {
        projectAdapter.removeOne(state, action.payload);
      })
      .addCase(deleteProject.rejected, () => { })
      .addCase(publishProject.pending, () => { })
      .addCase(publishProject.fulfilled, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.payload,
          changes: { published: true },
        });
      })
      .addCase(publishProject.rejected, () => { })
      .addCase(unpublishProject.pending, () => { })
      .addCase(unpublishProject.fulfilled, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.payload,
          changes: { published: false },
        });
      })
      .addCase(unpublishProject.rejected, () => { })
      .addCase(fetchProject.pending, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.meta.arg,
          changes: { status: "pending" },
        });
      })
      .addCase(fetchProject.rejected, (state, action) => {
        projectAdapter.updateOne(state, {
          id: action.meta.arg,
          changes: { status: "failure" },
        });
      })
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

export const { optimisticPatchProject } = projectSlice.actions;
export default projectSlice.reducer;
