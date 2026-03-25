import z from "zod/v4";
import type { Project, ProjectPatch } from "../../features/project/project";
import type { Furniture } from "../../features/furniture/slice";
import type { Plan } from "../../features/plan/entities";

export const AccountSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.email(),
  avatar_path: z.string(),
});

export const FurnitureSchema = z.object({
  id: z.string(),
  name: z.string(),
  width: z.number(),
  height: z.number(),
  depth: z.number(),
  mount: z.literal(["floor", "ceiling", "wall"]),
  model_path: z.string(),
  icon_path: z.string(),
  thumbnail_path: z.string(),
  meta: z.record(z.string(), z.any()),
});

export const PlanSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  name: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  content: z.object({
    furniture: z.record(
      z.string(),
      z.object({
        id: z.string(),
        furniture_id: z.string(),
        x: z.number(),
        y: z.number(),
        z: z.number(),
        yaw: z.number(),
      }),
    ),
    areas: z.record(
      z.string(),
      z.object({
        id: z.string(),
        type: z.string(),
        x: z.number(),
        y: z.number(),
        w: z.number(),
        h: z.number(),
      }),
    ),
  }),
});

export const ProjectSchema = z.object({
  id: z.string(),
  account_id: z.string(),
  name: z.string(),
  description: z.string(),
  published: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  content: z.object({
    walls: z.record(
      z.string(),
      z.object({
        id: z.string(),
        x1: z.number(),
        y1: z.number(),
        x2: z.number(),
        y2: z.number(),
      }),
    ),
    windows: z.record(
      z.string(),
      z.object({
        id: z.string(),
        wall_id: z.string(),
        x: z.number(),
        y: z.number(),
        w: z.number(),
        h: z.number(),
      }),
    ),
    doors: z.record(
      z.string(),
      z.object({
        id: z.string(),
        wall_id: z.string(),
        x: z.number(),
        w: z.number(),
        h: z.number(),
      }),
    ),
    wet_areas: z.record(
      z.string(),
      z.object({
        id: z.string(),
        x: z.number(),
        y: z.number(),
        w: z.number(),
        h: z.number(),
      }),
    ),
  }),
});

export type ServerAccount = z.infer<typeof AccountSchema>;
export type ServerFurniture = z.infer<typeof FurnitureSchema>;
export type ServerPlan = z.infer<typeof PlanSchema>;
export type ServerProject = z.infer<typeof ProjectSchema>;

function mapDict<A, B>(
  a: Record<string, A>,
  mapper: (v: A) => B,
): Record<string, B> {
  const b: Record<string, B> = {};
  for (const [k, v] of Object.entries(a)) {
    b[k] = mapper(v);
  }
  return b;
}

export function mapProject(project: ServerProject, etag: string): Project {
  return {
    id: project.id,
    accountId: project.account_id,
    name: project.name,
    description: project.description,
    published: project.published,
    dtCreated: project.created_at,
    dtUpdated: project.updated_at,
    content: {
      walls: project.content.walls,
      doors: mapDict(project.content.doors, (door) => {
        return {
          id: door.id,
          wallId: door.wall_id,
          x: door.x,
          w: door.w,
          h: door.h,
        };
      }),
      windows: mapDict(project.content.windows, (window) => {
        return {
          id: window.id,
          wallId: window.wall_id,
          x: window.x,
          y: window.y,
          w: window.w,
          h: window.h,
        };
      }),
      wetAreas: project.content.wet_areas,
    },
    etag: etag,
  };
}

export function mapPlan(plan: ServerPlan, etag: string): Plan {
  return {
    id: plan.id,
    name: plan.name,
    projectId: plan.project_id,
    content: {
      furniture: mapDict(plan.content.furniture, (f) => {
        return {
          id: f.id,
          furnitureId: f.furniture_id,
          x: f.x,
          y: f.y,
          z: f.z,
          yaw: f.yaw,
        };
      }),
      areas: plan.content.areas,
    },
    dtCreated: plan.created_at,
    dtUpdated: plan.updated_at,
    etag: etag,
  };
}

export function mapFurniture(furniture: ServerFurniture): Furniture {
  return {
    id: furniture.id,
    name: furniture.name,
    width: furniture.width,
    height: furniture.height,
    depth: furniture.depth,
    mount: furniture.mount,
    modelPath: furniture.model_path,
    thumbnailPath: furniture.thumbnail_path,
    iconPath: furniture.icon_path,
    meta: furniture.meta,
  };
}

export function mapProjectPatch(patch: ProjectPatch): any {
  const windows: any = {};
  if (patch.content?.windows) {
    for (const [key, window] of Object.entries(patch.content.windows)) {
      if (!window) {
        windows[key] = window;
      } else {
        windows[key] = {
          id: key,
          wall_id: window.wallId,
          x: window.x,
          y: window.y,
          w: window.w,
          h: window.h,
        };
      }
    }
  }
  return {
    name: patch.name,
    description: patch.description,
    content: {
      windows: windows,
      walls: patch.content?.walls || {},
      doors: {},
      wet_areas: {},
    },
  };
}
