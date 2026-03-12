import { createEntityAdapter, createSlice } from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";
import { createAppAsyncThunk } from "../../app/withTypes";
import { CONFIG } from "../../shared/config";

export interface Furniture {
  id: string;
  name: string;
  width: number;
  height: number;
  depth: number;
  mount: string;
  model_path: string;
  icon_path: string;
  thumbnail_path: string;
  meta: any;
}

export const fetchFurniture = createAppAsyncThunk(
  "furniture/fetchFurniture",
  async (filters: { name: string, area: string }) => {
    const { name, area } = filters;
    const url = new URL(`${CONFIG.gateway.baseURL}/catalog/search`);
    name !== "" && url.searchParams.append("name", name);
    area !== "" && url.searchParams.append("area", area);
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error("failed to fetch furniture");
    }
    const data = (await resp.json()).furniture as Furniture[];
    return data;
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
      furnitureAdapter.setAll(state, action.payload);
    })
  },
});

const selectors = furnitureAdapter.getSelectors<RootState>(state => state.furniture);
export const selectAllFurniture = selectors.selectAll
export default furnitureSlice.reducer;
