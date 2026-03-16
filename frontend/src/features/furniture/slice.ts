import { createEntityAdapter, createSlice } from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";
import { createAppAsyncThunk } from "../../app/withTypes";
import { Client } from "../../shared/client";

export interface Furniture {
  id: string;
  name: string;
  width: number;
  height: number;
  depth: number;
  mount: string;
  modelPath: string;
  iconPath: string;
  thumbnailPath: string;
  meta: any;
}

export const fetchFurniture = createAppAsyncThunk(
  "furniture/fetchFurniture",
  async ({
    name,
    area,
    limit,
    cursor,
  }: {
    name: string;
    area: string;
    limit: number | null;
    cursor: string | null;
  }) => {
    return Client.catalog.searchFurniture(name, area, limit, cursor);
  },
);

export const fetchFurnitureById = createAppAsyncThunk(
  "furniture/fetchFurnitureById",
  async (furnitureId: string) => {
    return Client.catalog.getFurnitureById(furnitureId);
  },
);

const furnitureAdapter = createEntityAdapter<Furniture, string>({
  selectId: (furniture) => furniture.id,
});

const furnitureSlice = createSlice({
  name: "furniture",
  initialState: furnitureAdapter.getInitialState(),
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchFurniture.fulfilled, (state, action) => {
      furnitureAdapter.addMany(state, action.payload.furniture);
    });
  },
});

const selectors = furnitureAdapter.getSelectors<RootState>(
  (state) => state.furniture,
);
export const selectAllFurniture = selectors.selectAll;
export const selectFurnitureById = selectors.selectById;
export default furnitureSlice.reducer;
