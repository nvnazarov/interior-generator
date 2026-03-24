import { z } from "zod/v4"

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

export const RawProjectsArraySchema = z.array(RawProjectSchema);

export type RawProject = z.infer<typeof RawProjectSchema>