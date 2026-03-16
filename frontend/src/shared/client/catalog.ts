import z from "zod";
import { CONFIG } from "../config";
import { FurnitureSchema, mapFurniture } from "./schema";
import type { Furniture } from "../../features/furniture/slice";

export const SearchFurnitureResponseSchema = z.object({
  meta: z.object({
    cursor: z.string().nullable(),
  }),
  furniture: z.array(FurnitureSchema),
});

export interface SearchFurnitureResult {
  meta: {
    cursor: string | null;
  };
  furniture: Furniture[];
}

export type SearchFurnitureResponse = z.infer<
  typeof SearchFurnitureResponseSchema
>;

export const CatalogClient = {
  searchFurniture: async (
    name: string,
    area: string,
    limit: number | null = null,
    cursor: string | null = null,
  ): Promise<SearchFurnitureResult> => {
    const url = new URL(`${CONFIG.gateway.baseURL}/catalog/search`);
    cursor !== null && url.searchParams.append("cursor", cursor);
    name !== "" && url.searchParams.append("name", name);
    area !== "" && url.searchParams.append("area", area);
    limit !== null && url.searchParams.append("limit", limit.toString());
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error("search furniture: response is not ok");
    }
    const json = await resp.json();
    const result = SearchFurnitureResponseSchema.parse(json);
    return {
      meta: {
        cursor: result.meta.cursor,
      },
      furniture: result.furniture.map((f) => mapFurniture(f)),
    };
  },
  getFurnitureById: async (id: string): Promise<Furniture> => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/furniture/${id}`);
    if (!resp.ok) {
      throw new Error("get furniture by id: response is not ok");
    }
    const json = await resp.json();
    return mapFurniture(FurnitureSchema.parse(json));
  },
};
