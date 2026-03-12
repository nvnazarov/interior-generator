import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";
import { createAuthClient } from "better-auth/client";
import { CONFIG } from "../../shared/config";

export interface Account {
  name: string;
  email: string;
  avatar: string | null;
}

export interface AccountState {
  data: Account | null;
  status: "idle" | "pending" | "success" | "failure";
}

export interface SignInPayload {
  email: string;
  password: string;
}

export interface SignInError {
  code: "INVALID_EMAIL" | "INCORRECT_EMAIL_OR_PASSWORD" | "OTHER";
}

export interface SignUpPayload {
  name: string;
  email: string;
  password: string;
}

export interface SignUpError {
  code:
  | "VALIDATION_ERROR"
  | "USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL"
  | "PASSWORD_TOO_SHORT"
  | "OTHER";
}

export const authClient = createAuthClient({
  baseURL: `${CONFIG.gateway.baseURL}/auth`,
});

export const signUp = createAsyncThunk<
  Account,
  SignUpPayload,
  { rejectValue: SignUpError }
>("account/signUp", async (payload: SignUpPayload, { rejectWithValue }) => {
  const resp = await authClient.signUp.email(payload);
  if (resp.error) {
    if (resp.error.code == "USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL") {
      return rejectWithValue({ code: "USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL" });
    }
    if (resp.error.code == "PASSWORD_TOO_SHORT") {
      return rejectWithValue({ code: "PASSWORD_TOO_SHORT" });
    }
    if (resp.error.code == "VALIDATION_ERROR") {
      return rejectWithValue({ code: "VALIDATION_ERROR" });
    }
    return rejectWithValue({ code: "OTHER" });
  }
  return {
    email: resp.data.user.email,
    name: resp.data.user.name,
    avatar: resp.data.user.image || null,
  };
});

export const signIn = createAsyncThunk<
  Account,
  SignInPayload,
  { rejectValue: SignInError }
>("account/singIn", async (payload: SignInPayload, { rejectWithValue }) => {
  const resp = await authClient.signIn.email(payload);
  if (resp.error) {
    if (resp.error.status == 401) {
      return rejectWithValue({ code: "INCORRECT_EMAIL_OR_PASSWORD" });
    }
    if (resp.error.code == "INVALID_EMAIL") {
      return rejectWithValue({ code: "INVALID_EMAIL" });
    }
    return rejectWithValue({ code: "OTHER" });
  }
  return {
    email: resp.data.user.email,
    name: resp.data.user.name,
    avatar: resp.data.user.image || null,
  };
});

export const signOut = createAsyncThunk("account/signOut", async () => {
  await authClient.signOut();
});

// export const update = createAsyncThunk(
//   "account/update",
//   async (payload: UpdatePayload) => {
//     const resp = await authClient.updateUser(payload);
//     if (!resp.data) {
//       throw Error("data is undefined or null");
//     }
//     return {
//       name: payload.name,
//     };
//   },
// )

const initialState: AccountState = { data: null, status: "idle" };

const accountSlice = createSlice({
  name: "account",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(signUp.pending, (state) => {
        state.status = "pending";
      })
      .addCase(signUp.fulfilled, (state, action) => {
        state.status = "success";
        state.data = action.payload;
      })
      .addCase(signUp.rejected, (state) => {
        state.status = "failure";
      })
      .addCase(signIn.pending, (state) => {
        state.status = "pending";
      })
      .addCase(signIn.fulfilled, (state, action) => {
        state.status = "success";
        state.data = action.payload;
      })
      .addCase(signIn.rejected, (state) => {
        state.status = "failure";
      })
      .addCase(signOut.pending, (state) => {
        state.status = "pending";
      })
      .addCase(signOut.fulfilled, (state) => {
        state.status = "success";
        state.data = null;
      })
      .addCase(signOut.rejected, (state) => {
        state.status = "failure";
      });
  },
});

export const selectData = (state: RootState) => state.account.data;
export const selectStatus = (state: RootState) => state.account.status;

export default accountSlice.reducer;
