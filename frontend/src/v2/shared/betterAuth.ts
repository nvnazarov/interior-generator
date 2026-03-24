import { createAuthClient } from "better-auth/client";
import { Config } from "./config";

export const authClient = createAuthClient({
  baseURL: `${Config.gateway.baseUrl}/api/auth`,
});
