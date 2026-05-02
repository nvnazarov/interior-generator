import "dotenv/config";
import { server } from "./server.ts";
import { config } from "./config.ts";
import { log } from "./log";

log.info({ config: config });

server.listen(config.port, config.host, () => {
  log.info({ "msg": `listening on port ${config.port}` });
});
