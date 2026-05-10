import { z } from "zod/v4";

export const RawProjectSchema = z.union([
  z.object({
    id: z.string(),
    account_id: z.string(),
    name: z.string(),
    published: z.literal(false),
    published_at: z.null(),
    plans_count: z.number(),
    plans_limit: z.number(),
    created_at: z.string(),
    updated_at: z.string(),
    content: z.object({
      walls: z.record(
        z.string(),
        z.object({
          x1: z.number(),
          y1: z.number(),
          x2: z.number(),
          y2: z.number(),
        }),
      ),
      windows: z.record(
        z.string(),
        z.object({
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
          wall_id: z.string(),
          x: z.number(),
          w: z.number(),
          h: z.number(),
        }),
      ),
      wet_areas: z.record(
        z.string(),
        z.object({
          points: z.array(
            z.object({
              x: z.number(),
              y: z.number(),
            }),
          ),
        }),
      ),
    }),
  }),
  z.object({
    id: z.string(),
    account_id: z.string(),
    name: z.string(),
    published: z.literal(true),
    published_at: z.string(),
    plans_count: z.number(),
    plans_limit: z.number(),
    created_at: z.string(),
    updated_at: z.string(),
    content: z.object({
      walls: z.record(
        z.string(),
        z.object({
          x1: z.number(),
          y1: z.number(),
          x2: z.number(),
          y2: z.number(),
        }),
      ),
      windows: z.record(
        z.string(),
        z.object({
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
          wall_id: z.string(),
          x: z.number(),
          w: z.number(),
          h: z.number(),
        }),
      ),
      wet_areas: z.record(
        z.string(),
        z.object({
          points: z.array(
            z.object({
              x: z.number(),
              y: z.number(),
            }),
          ),
        }),
      ),
    }),
  }),
]);

export const RawPlanSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  name: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  content: z.object({
    furniture: z.record(
      z.string(),
      z.object({
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
        type: z.literal([
          "kitchen",
          "livingroom",
          "bedroom",
          "bathroom",
          "hallway",
        ]),
        points: z.array(
          z.object({
            x: z.number(),
            y: z.number(),
          }),
        ),
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
  mount: z.string(),
  meta: z.record(z.string(), z.any()),
});

export const RawPromptSchema = z.object({
  id: z.string(),
  text: z.string(),
  project_id: z.string(),
  base: z
    .object({
      furniture: z.record(
        z.string(),
        z.object({
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
          type: z.literal([
            "kitchen",
            "livingroom",
            "bedroom",
            "bathroom",
            "hallway",
          ]),
          points: z.array(
            z.object({
              x: z.number(),
              y: z.number(),
            }),
          ),
        }),
      ),
    })
    .nullable(),
  patches: z.array(
    z.object({
      name: z.string().optional(),
      content: z
        .object({
          furniture: z
            .record(
              z.string(),
              z
                .object({
                  furniture_id: z.string().optional(),
                  x: z.number().optional(),
                  y: z.number().optional(),
                  z: z.number().optional(),
                  yaw: z.number().optional(),
                })
                .nullable(),
            )
            .optional(),
          areas: z
            .record(
              z.string(),
              z
                .object({
                  type: z
                    .literal([
                      "kitchen",
                      "livingroom",
                      "bedroom",
                      "bathroom",
                      "hallway",
                    ])
                    .optional(),
                  points: z
                    .array(
                      z.object({
                        x: z.number(),
                        y: z.number(),
                      }),
                    )
                    .optional(),
                })
                .nullable(),
            )
            .optional(),
        })
        .optional(),
    }),
  ),
  status: z.literal(["pending", "success", "failed"]),
  dt_created: z.string(),
  dt_done: z.string().nullable(),
});

export const AccountSchema = z.object({
  name: z.string(),
  image: z.string().nullable(),
});

export const RawProjectsArraySchema = z.array(RawProjectSchema);
export const RawPlansArraySchema = z.array(RawPlanSchema);
export const RawFurnitureArraySchema = z.array(RawFurnitureSchema);
export const RawPromptsArraySchema = z.array(RawPromptSchema);

export const FurnitureCatalogResponseSchema = z.object({
  furniture: RawFurnitureArraySchema,
  meta: z.object({
    cursor: z.string().nullable(),
  }),
});

export type RawProject = z.infer<typeof RawProjectSchema>;
export type RawPlan = z.infer<typeof RawPlanSchema>;
export type RawFurniture = z.infer<typeof RawFurnitureSchema>;
export type RawPrompt = z.infer<typeof RawPromptSchema>;
export type FurnitureCatalogResponse = z.infer<
  typeof FurnitureCatalogResponseSchema
>;
