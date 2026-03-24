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
  baseQuery: fetchBaseQuery({ baseUrl: apiBaseUrl }),
  endpoints: (builder) => ({
    getAllOwnedProjects: builder.query<Project[], void>({
      query: () => "projects",
      rawResponseSchema: RawProjectsArraySchema,
      transformResponse: (response: RawProject[]) => response.map(raw => ({
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
      }))
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
          windows: mapById(raw.content.windows, (w) => ({ wallId: w.id, x: w.x, y: w.y, w: w.w, h: w.h })),
          doors: mapById(raw.content.doors, (d) => ({ wallId: d.id, x: d.x, w: d.w, h: d.h })),
          wetAreas: raw.content.wet_areas,
        },
        published: raw.published,
        revision: meta?.response?.headers.get("etag") || "",
        dtCreated: raw.created_at,
        dtUpdated: raw.updated_at,
      })
    }),
    getAllPlansInProject: builder.query<Plan[], string>({
      query: (projectId: string) => `projects/${projectId}/plans`
    }),
    getPlanById: builder.query<Plan, string>({
      query: (planId: string) => `plans/${planId}`
    })
  })
})

export default api;
export const {
  useGetAllOwnedProjectsQuery,
  useGetProjectByIdQuery,
  useGetPlanByIdQuery,
  useGetAllPlansInProjectQuery,
} = api;