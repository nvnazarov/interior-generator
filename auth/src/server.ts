import express, { Express } from "express";
import { toNodeHandler } from "better-auth/node";
import { Auth } from "better-auth";

export function createServer(auth: Auth): Express {
  const server = express();
  server.all("/api/auth/*splat", toNodeHandler(auth));
  server.use(express.json());
  return server;
}
