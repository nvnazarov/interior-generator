import { z } from "zod/v4";

export const RawProjectSchema = z.object({
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

export const RawFurnitureSchema = z.object({
  id: z.string(),
  name: z.string(),
  width: z.number(),
  height: z.number(),
  depth: z.number(),
  model_path: z.string(),
  thumbnail_path: z.string(),
  icon_path: z.string(),
  meta: z.record(z.string(), z.any()),
});

export const RawProjectsArraySchema = z.array(RawProjectSchema);
export const RawFurnitureArraySchema = z.array(RawFurnitureSchema);

export const FurnitureCatalogResponseSchema = z.object({
  furniture: RawFurnitureArraySchema,
  meta: z.object({
    cursor: z.string().nullable(),
  }),
});

export type RawProject = z.infer<typeof RawProjectSchema>;
export type RawFurniture = z.infer<typeof RawFurnitureSchema>;
export type FurnitureCatalogResponse = z.infer<
  typeof FurnitureCatalogResponseSchema
>;
