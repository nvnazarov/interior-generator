import { expect, test, beforeAll, afterAll } from "vitest";
import { startDb, stopDb } from "../tests/setup";
import request from "supertest";
import { execSync } from "child_process";

let server: ReturnType<typeof import("./server").server.listen>;

beforeAll(async () => {
  const dbPort = await startDb({ db: "test", user: "test", password: "test" });

  process.env.AUTH__POSTGRES__HOST = "localhost";
  process.env.AUTH__POSTGRES__USER = "test";
  process.env.AUTH__POSTGRES__PASSWORD = "test";
  process.env.AUTH__POSTGRES__DB = "test";
  process.env.AUTH__POSTGRES__PORT = dbPort.toString();
  process.env.AUTH__BETTER_AUTH__BASE_URL = "http://localhost:4000/auth";
  process.env.AUTH__BETTER_AUTH__SECRET = "xm1bkH9yb7Kt1TYsjhjxjq86wTVUn0OC";
  process.env.AUTH__BETTER_AUTH__TRUSTED_ORIGINS = "http://localhost:4000";

  execSync("npx prisma migrate deploy", { stdio: "inherit" });

  const serverModule = await import("./server");
  server = serverModule.server.listen(4000);
}, 60000);

afterAll(async () => {
  await stopDb();
  if (server) {
    server.close();
  }
}, 60000);

test("health", async () => {
  await request(server).get("/health").expect(204);
});

test("auth scenario", async () => {
  const agent = request.agent(server);

  const user = await agent
    .post("/auth/sign-up/email")
    .send({
      name: "test",
      email: "test@test.com",
      password: "test-password",
    })
    .expect(200)
    .then((response) => {
      expect(response.body.user).toBeDefined();
      return response.body.user;
    });

  await request(server)
    .get(`/accounts/${user.id}`)
    .expect(200)
    .then((response) => {
      expect(response.body.image).toBeNull();
      expect(response.body.name).toBe("test");
    });

  await request(server).get("/auth").expect(401);
  await agent.get("/auth").expect(200).expect("x-account-id", user.id);

  await agent
    .post("/auth/delete-user")
    .send({ password: "test-password" })
    .expect(200);

  await request(server).get(`/accounts/${user.id}`).expect(404);
});
