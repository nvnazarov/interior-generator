import express from "express";
import { fromNodeHeaders, toNodeHandler } from "better-auth/node";
import { auth } from "./auth";
import { prisma } from "./prisma";
import { log } from "./log";

export const server = express();
server.use((req, res, next) => {
  next();
  res.on("finish", () => {
    log.info({ method: req.method, url: req.url, status: res.statusCode });
  })
});
server.all("/auth/*splat", toNodeHandler(auth));
server.get("/auth", async (req, res) => {
  try {
    const headers = fromNodeHeaders(req.headers);
    const session = await auth.api.getSession({ headers });
    if (session && session.user) {
      res.setHeader("x-account-id", session.user.id).status(200).send();
    } else {
      res.status(401).json({ error: "Unauthorized" });
    }
  } catch (error) {
    log.error({ msg: "error: getting session", error });
    res.status(500).json({ error: "Internal server error" });
  }
});
server.get("/accounts/:id", async (req, res) => {
  try {
    const user = await prisma.user.findFirst({
      select: { name: true, image: true },
      where: { id: req.params.id },
    });
    if (user === null) {
      res.status(404).json({ error: "Account not found" });
    } else {
      res.status(200).json(user);
    }
  } catch (error) {
    log.error({ msg: "error: getting user", error });
    res.status(500).json({ error: "Internal server error" });
  }
});
server.get("/health", (_, res) => {
  res.sendStatus(204);
});
server.use(express.json());
