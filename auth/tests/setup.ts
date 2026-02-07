import {
  StartedPostgreSqlContainer,
  PostgreSqlContainer,
} from "@testcontainers/postgresql";

export let container: StartedPostgreSqlContainer;
export let dbUrl: string;

export async function startDb() {
  container = await new PostgreSqlContainer("postgres:17.5-alpine")
    .withDatabase("test")
    .withUsername("test")
    .withPassword("test")
    .start();

  dbUrl = container.getConnectionUri();
  process.env.DATABASE_URL = dbUrl;
}

export async function stopDb() {
  if (container) {
    await container.stop();
  }
}
