import {
  StartedPostgreSqlContainer,
  PostgreSqlContainer,
} from "@testcontainers/postgresql";

let container: StartedPostgreSqlContainer;

export async function startDb({
  db,
  user,
  password,
}: {
  db: string;
  user: string;
  password: string;
}): Promise<number> {
  container = await new PostgreSqlContainer("postgres:17.5-alpine")
    .withDatabase(db)
    .withUsername(user)
    .withPassword(password)
    .start();
  return container.getPort();
}

export async function stopDb() {
  if (container) {
    await container.stop();
  }
}
