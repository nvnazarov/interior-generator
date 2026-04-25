import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "../generated/prisma1/client";
import { config } from "./config";

const adapter = new PrismaPg({ connectionString: config.postgres.url });
export const prisma = new PrismaClient({ adapter });
