import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { AppState } from "../store";

type Account = {
  id: string;
  name: string;
  email: string;
  avatarUrl: string | null;
  dtCreated: string;
}

type AccountState = Account | null

const accountSlice = createSlice({
  name: "account",
  initialState: null as AccountState,
  reducers: {
    accountRestored(_, action: PayloadAction<Account>) {
      return action.payload
    },
    accountUpdated(state, action: PayloadAction<Partial<Account>>) {
      if (state) {
        return { ...state, ...action.payload }
      } else {
        throw new Error("state was null when 'updated' reducer was called")
      }
    },
    accountDeleted(state) {
      state = null
    }
  },
})

export default accountSlice.reducer;
export const { accountRestored, accountUpdated, accountDeleted } = accountSlice.actions;
export const selectMyAccount = (state: AppState) => state.account;
export type { Account };