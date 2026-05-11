import type { Action, ThunkAction } from "@reduxjs/toolkit";
import { configureStore } from "@reduxjs/toolkit";
import account from "./account/slice";
import notifications from "./notifications/slice";
import projectEditor from "./project-editor/slice";
import planEditor from "./plan-editor/slice";
import api from "./api/slice";

export const store = configureStore({
  reducer: {
    account,
    projectEditor,
    planEditor,
    notifications,
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

export type AppStore = typeof store;
export type AppState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
export type AppThunk<ThunkReturnType = void> = ThunkAction<
  ThunkReturnType,
  AppState,
  unknown,
  Action
>;
