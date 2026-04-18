import { server } from "./server.ts";
import { config } from "./config.ts";

server.listen(config.port, () => {
  console.log(`listening on port ${config.port}`);
});
