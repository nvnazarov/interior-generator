import express from "express";
import { fromNodeHeaders, toNodeHandler } from "better-auth/node";
import { auth } from "./auth";
import { prisma } from "./prisma";

export const server = express();
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
server.get("/accounts/:id", async (req, res) => {
  const user = await prisma.user.findFirst({ select: { name: true, image: true }, where: { id: req.params.id } })
  if (user === null) {
    res.status(404).json({ error: "Account not found" });
  } else {
    res.status(200).json(user);
  }
})
server.get("/health", (_, res) => {
  res.sendStatus(204);
});
server.use(express.json());
