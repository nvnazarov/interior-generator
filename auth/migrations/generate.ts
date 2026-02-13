import { PostgreSqlContainer } from "@testcontainers/postgresql";
import { createAuth } from "../src/lib/auth.ts";
import { getMigrations } from "better-auth/db";
import { PostgresConfig } from "../src/config.ts";

const container = await new PostgreSqlContainer("postgres:17.5-alpine")
  .withDatabase("test")
  .withUsername("test")
  .withPassword("test")
  .start();
const config = {
  port: "8080",
  postgres: new PostgresConfig(
    container.getHost(),
    container.getPort().toString(),
    container.getDatabase(),
    container.getUsername(),
    container.getPassword(),
  ),
  betterAuth: {
    baseURL: "http://localhost:8080",
    trustedOrigins: [],
  },
};
const auth = createAuth(config);
const migrations = await getMigrations(auth.options);
const script = await migrations.compileMigrations();
console.log(script);
