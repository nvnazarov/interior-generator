import express, { Express } from "express";
import { fromNodeHeaders, toNodeHandler } from "better-auth/node";
import { Auth } from "better-auth";

export function createServer(auth: Auth): Express {
  const server = express();
  server.all("/api/auth/*splat", toNodeHandler(auth));
  server.get("/api/me", async (req, res) => {
    try {
      const headers = fromNodeHeaders(req.headers)
      const session = await auth.api.getSession({ headers })
      if (session && session.user) {
        res.setHeader("x-account-id", session.user.id).status(200).send()
      } else {
        res.status(401).json({ error: "Unauthorized" })
      }
    } catch (error) {
      console.error("error: getting session", error);
      res.status(500).json({ error: "Internal server error" });
    }
  })
  server.get("/health", (_, res) => {
    res.sendStatus(204);
  });
  server.use(express.json());
  return server;
}
