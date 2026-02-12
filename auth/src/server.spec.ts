import { describe, it, expect, beforeAll, afterAll } from "vitest";
import request from "supertest";
import { createServer } from "./server.ts";
import { createAuth } from "./lib/auth.ts";
import { Config, PostgresConfig } from "./config.ts";
import {
  StartedPostgreSqlContainer,
  PostgreSqlContainer,
} from "@testcontainers/postgresql";
import { getMigrations } from "better-auth/db";
import { Auth } from "better-auth";
import { Express } from "express";

const POSTGRES_START_TIMEOUT_MS = 60 * 1000

describe("server", () => {
  let config: Config
  let container: StartedPostgreSqlContainer
  let auth: Auth
  let server: Express

  beforeAll(async () => {
    container = await new PostgreSqlContainer("postgres:17.5-alpine")
      .withDatabase("test")
      .withUsername("test")
      .withPassword("test")
      .start();
    config = {
      port: "8080",
      postgres: new PostgresConfig(
        container.getHost(),
        container.getPort().toString(),
        container.getDatabase(),
        container.getUsername(),
        container.getPassword()
      ),
      betterAuth: {
        baseURL: "http://localhost:8080",
      },
    }
    auth = createAuth(config)
    const migrations = await getMigrations(auth.options)
    await migrations.runMigrations()
    server = createServer(auth);
  }, POSTGRES_START_TIMEOUT_MS)

  afterAll(async () => {
    // TODO(nvnazarov@edu.hse.ru): fix a strange bug when stopping a container
    // if (container) {
    //   await container.stop();
    // }
  })

  it("registers a user", async () => {
    const resp = await request(server).post("/api/auth/sign-up/email").send({
      name: "test",
      email: "test@test.com",
      password: "password123",
    });

    expect(resp.status).toBe(200);
    expect(resp.body.user.email).toBe("test@test.com");
  })
  it("authenticates a user", async () => {
    const res = await request(server)
      .post("/api/auth/sign-in/email")
      .send({
        email: "test@test.com",
        password: "password123",
      });

    expect(res.status).toBe(200);
    expect(res.body.user.email).toBe("test@test.com");
  })
})