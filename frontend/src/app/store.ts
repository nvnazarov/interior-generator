import type { Action, ThunkAction } from "@reduxjs/toolkit";
import { configureStore } from "@reduxjs/toolkit";
import accountReducer from "../features/account/accountSlice";
import projectsReducer from "../features/project/projectSlice";
import furnitureReducer from "../features/furniture/furnitureSlice";

export const store = configureStore({
  reducer: {
    account: accountReducer,
    projects: projectsReducer,
    furniture: furnitureReducer,
  },
});

export type AppStore = typeof store;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
export type AppThunk<ThunkReturnType = void> = ThunkAction<
  ThunkReturnType,
  RootState,
  unknown,
  Action
>;
