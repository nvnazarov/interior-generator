import "dotenv/config";
import { server } from "./server.ts";
import { config } from "./config.ts";

server.listen(config.port, config.host, () => {
  console.log(`listening on port ${config.port}`);
});
