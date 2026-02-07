import { createServer } from "./server.ts";
import { loadConfigFromEnv } from "./config.ts";
import { createAuth } from "./lib/auth.ts";

const config = loadConfigFromEnv();
const auth = createAuth(config);
const server = createServer(auth);
server.listen(config.port, () => {
  console.log(`listening on port ${config.port}`);
});
