import { ProjectsClient } from "./projects";
import { ExporterClient } from "./exporter";
import { CatalogClient } from "./catalog";
import { AuthClient } from "./auth";
import { GeneratorClient } from "./generator";
import { AssetsClient } from "./assets";
import { PlansClient } from "./plans";

export const Client = {
  projects: ProjectsClient,
  plans: PlansClient,
  exporter: ExporterClient,
  catalog: CatalogClient,
  auth: AuthClient,
  generator: GeneratorClient,
  assets: AssetsClient,
};
