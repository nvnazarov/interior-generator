import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type {
  Furniture,
  Project,
  Plan,
  ProjectPatch,
  PlanPatch,
  Prompt,
} from "./entities";
import {
  FurnitureCatalogResponseSchema,
  RawFurnitureSchema,
  RawPlansArraySchema,
  RawPlanSchema,
  RawProjectsArraySchema,
  RawProjectSchema,
  RawPromptsArraySchema,
} from "./schema";
import type {
  FurnitureCatalogResponse,
  RawFurniture,
  RawPlan,
  RawProject,
  RawPrompt,
} from "./schema";
import { mapById } from "./util";
import { Config } from "../../shared/config";
import { UrlUtil } from "../../shared/util";

const apiBaseUrl = UrlUtil.noRightSlash(Config.gateway.baseUrl) + "/api";

const api = createApi({
  reducerPath: "api",
  tagTypes: ["Projects", "Plans", "Prompts"],
  baseQuery: fetchBaseQuery({ baseUrl: apiBaseUrl }),
  endpoints: (builder) => ({
    getAllOwnedProjects: builder.query<Project[], void>({
      query: () => "projects",
      rawResponseSchema: RawProjectsArraySchema,
      transformResponse: (response: RawProject[]) =>
        response.map((raw) => ({
          id: raw.id,
          accountId: raw.account_id,
          name: raw.name,
          description: raw.description,
          content: {
            walls: {},
            windows: {},
            doors: {},
            wetAreas: {},
          },
          published: raw.published,
          revision: "",
          dtCreated: raw.created_at,
          dtUpdated: raw.updated_at,
        })),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "Projects", id }) as const),
              { type: "Projects", id: "LIST" },
            ]
          : [{ type: "Projects", id: "LIST" }],
    }),
    getProjectById: builder.query<Project, string>({
      query: (projectId: string) => `projects/${projectId}`,
      rawResponseSchema: RawProjectSchema,
      transformResponse: (raw: RawProject, meta?: { response?: Response }) => ({
        id: raw.id,
        accountId: raw.account_id,
        name: raw.name,
        description: raw.description,
        content: {
          walls: raw.content.walls,
          windows: mapById(raw.content.windows, (w) => ({
            id: w.id,
            wallId: w.wall_id,
            x: w.x,
            y: w.y,
            w: w.w,
            h: w.h,
          })),
          doors: mapById(raw.content.doors, (d) => ({
            id: d.id,
            wallId: d.wall_id,
            x: d.x,
            w: d.w,
            h: d.h,
          })),
          wetAreas: raw.content.wet_areas,
        },
        published: raw.published,
        revision: meta?.response?.headers.get("etag") || "",
        dtCreated: raw.created_at,
        dtUpdated: raw.updated_at,
      }),
      providesTags: (result) => [{ type: "Projects", id: result?.id }],
    }),
    createProject: builder.mutation<Project, void>({
      query: () => ({
        url: "projects",
        method: "POST",
      }),
      rawResponseSchema: RawProjectSchema,
      transformResponse: (raw: RawProject, meta?: { response?: Response }) => ({
        id: raw.id,
        accountId: raw.account_id,
        name: raw.name,
        description: raw.description,
        content: {
          walls: raw.content.walls,
          windows: mapById(raw.content.windows, (w) => ({
            id: w.id,
            wallId: w.wall_id,
            x: w.x,
            y: w.y,
            w: w.w,
            h: w.h,
          })),
          doors: mapById(raw.content.doors, (d) => ({
            id: d.id,
            wallId: d.wall_id,
            x: d.x,
            w: d.w,
            h: d.h,
          })),
          wetAreas: raw.content.wet_areas,
        },
        published: raw.published,
        revision: meta?.response?.headers.get("etag") || "",
        dtCreated: raw.created_at,
        dtUpdated: raw.updated_at,
      }),
      invalidatesTags: [{ type: "Projects", id: "LIST" }],
    }),
    deleteProject: builder.mutation<void, string>({
      query: (id) => ({
        url: `projects/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, id) => [{ type: "Projects", id }],
    }),
    publishProject: builder.mutation<void, string>({
      query: (id) => ({
        url: `projects/${id}/publish`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, id) => [{ type: "Projects", id }],
    }),
    unpublishProject: builder.mutation<void, string>({
      query: (id) => ({
        url: `projects/${id}/unpublish`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, id) => [{ type: "Projects", id }],
    }),
    patchProject: builder.mutation<
      string,
      { id: string; revision: string; patch: ProjectPatch }
    >({
      query: ({ id, revision, patch }) => {
        const content = patch.content;
        const windows = content?.windows;
        const doors = content?.doors;
        return {
          url: `projects/${id}`,
          method: "PATCH",
          headers: {
            "if-match": revision,
          },
          body: {
            name: patch.name,
            description: patch.description,
            content:
              content === undefined
                ? undefined
                : {
                    walls: content.walls,
                    wet_areas: content.wetAreas,
                    windows:
                      windows &&
                      Object.entries(windows)
                        .map(([id, window]): [string, any] =>
                          window
                            ? [
                                id,
                                {
                                  id: id,
                                  wall_id: window?.wallId,
                                  x: window?.x,
                                  y: window?.y,
                                  w: window?.w,
                                  h: window?.h,
                                },
                              ]
                            : [id, null],
                        )
                        .reduce((acc, curr) => {
                          acc[curr[0]] = curr[1];
                          return acc;
                        }, {} as any),
                    doors:
                      doors &&
                      Object.entries(doors)
                        .map(([id, door]): [string, any] =>
                          door
                            ? [
                                id,
                                {
                                  id: id,
                                  wall_id: door?.wallId,
                                  x: door?.x,
                                  w: door?.w,
                                  h: door?.h,
                                },
                              ]
                            : [id, null],
                        )
                        .reduce((acc, curr) => {
                          acc[curr[0]] = curr[1];
                          return acc;
                        }, {} as any),
                  },
          },
        };
      },
      transformResponse: (_, meta) => {
        const revision = meta?.response?.headers.get("etag");
        if (!revision) {
          throw new Error(
            "error: transform response: server did not return etag header",
          );
        }
        return revision;
      },
      invalidatesTags: (_result, _error, { id }) => [{ type: "Projects", id }],
    }),
    getAllPlansInProject: builder.query<Plan[], string>({
      query: (projectId: string) => `projects/${projectId}/plans`,
      rawResponseSchema: RawPlansArraySchema,
      transformResponse: (response: RawPlan[]) =>
        response.map((raw) => ({
          id: raw.id,
          projectId: raw.project_id,
          name: raw.name,
          content: {
            furniture: {},
            areas: {},
          },
          revision: "",
          dtCreated: raw.created_at,
          dtUpdated: raw.updated_at,
        })),
      providesTags: (result, _error, projectId) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "Plans", id }) as const),
              { type: "Plans", id: `LIST:${projectId}` },
            ]
          : [{ type: "Plans", id: `LIST:${projectId}` }],
    }),
    getPlanById: builder.query<Plan, string>({
      query: (planId: string) => `plans/${planId}`,
      rawResponseSchema: RawPlanSchema,
      transformResponse: (raw: RawPlan, meta?: { response?: Response }) => ({
        id: raw.id,
        projectId: raw.project_id,
        name: raw.name,
        content: {
          areas: raw.content.areas,
          furniture: mapById(raw.content.furniture, (f) => ({
            id: f.id,
            furnitureId: f.furniture_id,
            x: f.x,
            y: f.y,
            z: f.z,
            yaw: f.yaw,
          })),
        },
        revision: meta?.response?.headers.get("etag") || "",
        dtCreated: raw.created_at,
        dtUpdated: raw.updated_at,
      }),
      providesTags: (result) => [{ type: "Plans", id: result?.id }],
    }),
    createPlan: builder.mutation<Plan, string>({
      query: (projectId: string) => ({
        url: `projects/${projectId}/plans`,
        method: "POST",
      }),
      rawResponseSchema: RawPlanSchema,
      transformResponse: (raw: RawPlan, meta?: { response?: Response }) => ({
        id: raw.id,
        projectId: raw.project_id,
        name: raw.name,
        content: {
          areas: raw.content.areas,
          furniture: mapById(raw.content.furniture, (f) => ({
            id: f.id,
            furnitureId: f.furniture_id,
            x: f.x,
            y: f.y,
            z: f.z,
            yaw: f.yaw,
          })),
        },
        revision: meta?.response?.headers.get("etag") || "",
        dtCreated: raw.created_at,
        dtUpdated: raw.updated_at,
      }),
      invalidatesTags: (_result, _error, projectId) => [
        { type: "Plans", id: `LIST:${projectId}` },
      ],
    }),
    deletePlan: builder.mutation<void, string>({
      query: (planId: string) => ({
        url: `plans/${planId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, id) => [{ type: "Plans", id }],
    }),
    patchPlan: builder.mutation<
      string,
      { id: string; revision: string; patch: PlanPatch }
    >({
      query: ({ id, revision, patch }) => {
        const content = patch.content;
        const furniture = content?.furniture;
        return {
          url: `plans/${id}`,
          method: "PATCH",
          headers: {
            "if-match": revision,
          },
          body: {
            name: patch.name,
            content:
              content === undefined
                ? undefined
                : {
                    areas: content.areas,
                    furniture:
                      furniture &&
                      Object.entries(furniture)
                        .map(([id, f]): [string, any] =>
                          f
                            ? [
                                id,
                                {
                                  id: id,
                                  furniture_id: f?.furnitureId,
                                  x: f?.x,
                                  y: f?.y,
                                  z: f?.z,
                                  yaw: f?.yaw,
                                },
                              ]
                            : [id, null],
                        )
                        .reduce((acc, curr) => {
                          acc[curr[0]] = curr[1];
                          return acc;
                        }, {} as any),
                  },
          },
        };
      },
      transformResponse: (_, meta) => {
        const revision = meta?.response?.headers.get("etag");
        if (!revision) {
          throw new Error(
            "error: transform response: server did not return etag header",
          );
        }
        return revision;
      },
      invalidatesTags: (_result, _error, { id }) => [{ type: "Plans", id }],
    }),
    getFurniture: builder.infiniteQuery<
      { furniture: Furniture[]; cursor?: string },
      { name?: string; area?: string; cursor?: string },
      string | undefined
    >({
      infiniteQueryOptions: {
        initialPageParam: undefined,
        getNextPageParam: (
          _lastPage,
          _allPages,
          _lastPageParam,
          _allPageParams,
          queryArg,
        ) => queryArg.cursor,
      },
      query: ({ queryArg }) => {
        const url = new URL(`http://localhost/catalog/search`);
        if (queryArg.cursor) {
          url.searchParams.append("cursor", queryArg.cursor);
        } else {
          if (queryArg.area) {
            url.searchParams.append("area", queryArg.area);
          }
          if (queryArg.name) {
            url.searchParams.append("name", queryArg.name);
          }
        }
        return url.pathname + url.search;
      },
      rawResponseSchema: FurnitureCatalogResponseSchema,
      transformResponse: (response: FurnitureCatalogResponse) => ({
        furniture: response.furniture.map((raw) => ({
          id: raw.id,
          name: raw.name,
          width: raw.width,
          height: raw.height,
          depth: raw.depth,
          modelPath: raw.model_path,
          thumbnailPath: raw.thumbnail_path,
          iconPath: raw.icon_path,
          mount: raw.mount,
          meta: raw.meta,
        })),
        cursor: response.meta.cursor || undefined,
      }),
    }),
    getFurnitureById: builder.query<Furniture, string>({
      query: (furnitureId: string) => `catalog/furniture/${furnitureId}`,
      rawResponseSchema: RawFurnitureSchema,
      transformResponse: (raw: RawFurniture) => ({
        id: raw.id,
        name: raw.name,
        width: raw.width,
        height: raw.height,
        depth: raw.depth,
        mount: raw.mount,
        modelPath: raw.model_path,
        iconPath: raw.icon_path,
        thumbnailPath: raw.thumbnail_path,
        meta: raw.meta,
      }),
    }),
    getPromptsForProject: builder.query<Prompt[], string>({
      query: (projectId: string) => `projects/${projectId}/prompts`,
      rawResponseSchema: RawPromptsArraySchema,
      transformResponse: (prompts: RawPrompt[]) =>
        prompts.map((raw) => ({
          id: raw.id,
          text: raw.text,
          projectId: raw.project_id,
          basePlanId: raw.base_plan_id,
          generatedPlansIds: raw.generated_plans_ids,
          status: raw.status,
          dtCreated: raw.dt_created,
          dtDone: raw.dt_done,
        })),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "Prompts", id }) as const),
              { type: "Prompts", id: "LIST" },
            ]
          : [{ type: "Prompts", id: "LIST" }],
    }),
    generatePlans: builder.mutation<
      Prompt,
      { projectId: string; text: string; basePlanId: string | null }
    >({
      query: ({ projectId, text, basePlanId }) => ({
        url: `projects/${projectId}/prompts`,
        method: "POST",
        body: {
          text,
          basePlanId,
        },
      }),
      rawResponseSchema: RawPlanSchema,
      transformResponse: (raw: RawPrompt) => ({
        id: raw.id,
        text: raw.text,
        projectId: raw.project_id,
        basePlanId: raw.base_plan_id,
        generatedPlansIds: raw.generated_plans_ids,
        status: raw.status,
        dtCreated: raw.dt_created,
        dtDone: raw.dt_done,
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "Prompts", id: `LIST:${projectId}` },
        { type: "Plans", id: `LIST:${projectId}` },
      ],
    }),
  }),
});

export default api;
export const {
  useGetAllOwnedProjectsQuery,
  useGetProjectByIdQuery,
  useLazyGetProjectByIdQuery,
  useCreateProjectMutation,
  useDeleteProjectMutation,
  usePublishProjectMutation,
  useUnpublishProjectMutation,
  usePatchProjectMutation,
  useGetAllPlansInProjectQuery,
  useLazyGetPlanByIdQuery,
  useCreatePlanMutation,
  useDeletePlanMutation,
  usePatchPlanMutation,
  useGetFurnitureInfiniteQuery,
  useGetFurnitureByIdQuery,
  useLazyGetFurnitureByIdQuery,
  useGeneratePlansMutation,
  useGetPromptsForProjectQuery,
  useLazyGetPromptsForProjectQuery,
} = api;
