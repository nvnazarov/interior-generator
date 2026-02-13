import { describe, it, expect } from "vitest";
import {
  BetterAuthConfig,
  loadConfigFromEnv,
  PostgresConfig,
} from "./config.ts";

describe("config", () => {
  it("loads environment", async () => {
    process.env.APP_PORT = "8001";
    process.env.APP_POSTGRES__HOST = "postgres";
    process.env.APP_POSTGRES__PORT = "5432";
    process.env.APP_POSTGRES__DB = "db";
    process.env.APP_POSTGRES__USER = "user";
    process.env.APP_POSTGRES__PASSWORD = "password";
    process.env.BETTER_AUTH_BASE_URL = "base";
    process.env.BETTER_AUTH_TRUSTED_ORIGINS =
      "http://localhost:3000,http://localhost:8080";

    const config = loadConfigFromEnv();

    expect(config.port).toBe("8001");
    expect(config.betterAuth).toEqual({
      baseURL: "base",
      trustedOrigins: ["http://localhost:3000", "http://localhost:8080"],
    } as BetterAuthConfig);
    expect(config.postgres).toEqual({
      host: "postgres",
      port: "5432",
      db: "db",
      user: "user",
      password: "password",
    } as PostgresConfig);
  });
});
