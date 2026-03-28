import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { Furniture, Project, Plan, ProjectPatch } from "./entities";
import {
  FurnitureCatalogResponseSchema,
  RawProjectsArraySchema,
  RawProjectSchema,
} from "./schema";
import type { FurnitureCatalogResponse, RawProject } from "./schema";
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
            content: content === undefined ? undefined : ({
              walls: content.walls,
              wet_areas: content.wetAreas,
              windows: windows && Object.entries(windows).map(([id, window]) => ({
                id: id,
                wall_id: window?.wallId,
                x: window?.x,
                y: window?.y,
                w: window?.w,
                h: window?.h,
              })).reduce((acc, curr) => {
                acc[curr.id] = curr
                return acc
              }, {} as any),
              doors: doors && Object.entries(doors).map(([id, door]) => ({
                id: id,
                wall_id: door?.wallId,
                x: door?.x,
                w: door?.w,
                h: door?.h,
              })).reduce((acc, curr) => {
                acc[curr.id] = curr
                return acc
              }, {} as any),
            })
          },
        }
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
          meta: raw.meta,
        })),
        cursor: response.meta.cursor || undefined,
      }),
    }),
  }),
});

export default api;
export const {
  useGetAllOwnedProjectsQuery,
  useLazyGetProjectByIdQuery,
  useGetPlanByIdQuery,
  useGetAllPlansInProjectQuery,
  useCreateProjectMutation,
  useDeleteProjectMutation,
  usePublishProjectMutation,
  useUnpublishProjectMutation,
  usePatchProjectMutation,
  useGetFurnitureInfiniteQuery,
} = api;
