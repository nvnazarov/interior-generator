import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { AppState } from "../store";
import moment from "moment";

export type Notification = {
  text: string;
  severity: "info" | "error";
  date: string;
};

const notificationsSlice = createSlice({
  name: "notifications",
  initialState: [] as Notification[],
  reducers: {
    notify(state, action: PayloadAction<Partial<Notification>>) {
      state.push({
        text: "",
        severity: "info",
        date: moment().toISOString(),
        ...action.payload,
      });
    },
  },
});

export const selectNotifications = (state: AppState) => state.notifications;
export const selectLastNotification = (state: AppState) =>
  state.notifications[state.notifications.length - 1];
export const { notify } = notificationsSlice.actions;
export default notificationsSlice.reducer;
