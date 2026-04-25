import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "./prisma.ts";
import { config } from "./config.ts";

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
  },
  user: {
    deleteUser: {
      enabled: true,
    },
  },
  baseURL: config.betterAuth.baseURL,
  trustedOrigins: config.betterAuth.trustedOrigins,
  database: prismaAdapter(prisma, { provider: "postgresql" }),
});
