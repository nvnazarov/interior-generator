import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { Project } from "./entities";
import type { Plan } from "../../../features/plan/entities";
import { RawProjectsArraySchema, RawProjectSchema } from "./schema";
import type { RawProject } from "./schema";
import { mapById } from "./util";
import { Config } from "../../shared/config";
import { UrlUtil } from "../../shared/util";

const apiBaseUrl = UrlUtil.noRightSlash(Config.gateway.baseUrl) + "/api";

const api = createApi({
  reducerPath: "api",
  tagTypes: ["Projects"],
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
            wallId: w.id,
            x: w.x,
            y: w.y,
            w: w.w,
            h: w.h,
          })),
          doors: mapById(raw.content.doors, (d) => ({
            wallId: d.id,
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
    }),
    getAllPlansInProject: builder.query<Plan[], string>({
      query: (projectId: string) => `projects/${projectId}/plans`,
    }),
    getPlanById: builder.query<Plan, string>({
      query: (planId: string) => `plans/${planId}`,
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
            wallId: w.id,
            x: w.x,
            y: w.y,
            w: w.w,
            h: w.h,
          })),
          doors: mapById(raw.content.doors, (d) => ({
            wallId: d.id,
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
  }),
});

export default api;
export const {
  useGetAllOwnedProjectsQuery,
  useGetProjectByIdQuery,
  useGetPlanByIdQuery,
  useGetAllPlansInProjectQuery,
  useCreateProjectMutation,
  useDeleteProjectMutation,
  usePublishProjectMutation,
  useUnpublishProjectMutation,
} = api;
