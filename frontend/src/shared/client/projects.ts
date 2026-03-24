import z from "zod";
import type { ProjectPatch } from "../../features/project/project";
import { CONFIG } from "../config";
import type { Project } from "../../features/project/project";
import { mapProject, mapProjectPatch, ProjectSchema } from "./schema";

export const ProjectsSchema = z.array(ProjectSchema);

export const ProjectsClient = {
  create: async (): Promise<Project> => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/projects`, {
      method: "POST",
    });
    if (!resp.ok) {
      throw new Error("create project: response is not ok");
    }
    const json = await resp.json();
    const etag = resp.headers.get("etag");
    if (!etag) {
      throw new Error("create project: etag is empty");
    }
    return mapProject(ProjectSchema.parse(json), etag);
  },
  getById: async (projectId: string): Promise<Project> => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/projects/${projectId}`);
    if (!resp.ok) {
      throw new Error("get project by id: response is not ok");
    }
    const json = await resp.json();
    const etag = resp.headers.get("etag");
    if (!etag) {
      throw new Error("get project by id: etag is empty");
    }
    return mapProject(ProjectSchema.parse(json), etag);
  },
  patch: async (
    projectId: string,
    patch: ProjectPatch,
    etag: string,
  ): Promise<string> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${projectId}`,
      {
        method: "PATCH",
        headers: {
          "if-match": etag,
          "content-type": "application/json",
        },
        body: JSON.stringify(mapProjectPatch(patch)),
      },
    );
    if (!resp.ok) {
      throw new Error("patch project: response is not ok");
    }
    const newEtag = resp.headers.get("etag");
    if (newEtag === null) {
      throw new Error("patch project: no etag returned");
    }
    return newEtag;
  },
  delete: async (projectId: string): Promise<void> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${projectId}`,
      {
        method: "DELETE",
      },
    );
    if (!resp.ok) {
      throw new Error("delete project: response is not ok");
    }
  },
  publish: async (projectId: string): Promise<void> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${projectId}/publish`,
      { method: "POST" },
    );
    if (!resp.ok) {
      throw new Error("publish project: response is not ok");
    }
  },
  unpublish: async (projectId: string): Promise<void> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${projectId}/unpublish`,
      { method: "POST" },
    );
    if (!resp.ok) {
      throw new Error("unpublish project: response is not ok");
    }
  },
  getAllOwned: async (): Promise<Project[]> => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/projects`);
    if (!resp.ok) {
      throw new Error("get all owned projects: response is not ok");
    }
    const json = await resp.json();
    return ProjectsSchema.parse(json).map((project) => mapProject(project, ""));
  },
};
