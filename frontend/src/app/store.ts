import type { Action, ThunkAction } from "@reduxjs/toolkit";
import { configureStore } from "@reduxjs/toolkit";
import accountReducer from "../features/account/accountSlice";
import {
  projectsReducer,
  projectEditorReducer,
} from "../features/project/slice";
import furnitureReducer from "../features/furniture/slice";
import plansReducer from "../features/plan/slice";

export const store = configureStore({
  reducer: {
    account: accountReducer,
    plans: plansReducer,
    projects: projectsReducer,
    projectEditor: projectEditorReducer,
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
