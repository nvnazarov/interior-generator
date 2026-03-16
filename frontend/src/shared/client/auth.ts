import { createAuthClient } from "better-auth/client";
import { CONFIG } from "../config";

export const AuthClient = createAuthClient({
  baseURL: `${CONFIG.gateway.baseURL}/auth`,
});
