import { betterAuth, Auth } from "better-auth";
import { Pool } from "pg";
import { Config } from "../config.ts";

export function createAuth(config: Config): Auth {
  return betterAuth({
    emailAndPassword: {
      enabled: true,
    },
    baseURL: config.betterAuth.baseURL,
    database: new Pool({
      connectionString: config.postgres.uri(),
    }),
  });
}
