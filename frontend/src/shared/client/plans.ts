import z from "zod";
import type { Plan, PlanPatch } from "../../features/plan/entities";
import { CONFIG } from "../config";
import { mapPlan, PlanSchema } from "./schema";

export const PlansSchema = z.array(PlanSchema);

export const PlansClient = {
  create: async (projectId: string): Promise<Plan> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${projectId}/plans`,
      {
        method: "POST",
      },
    );
    if (!resp.ok) {
      throw new Error("create plan: response is not ok");
    }
    const json = await resp.json();
    const etag = resp.headers.get("etag");
    if (!etag) {
      throw new Error("create plan: etag is empty");
    }
    return mapPlan(PlanSchema.parse(json), etag);
  },
  getById: async (planId: string): Promise<Plan> => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/plans/${planId}`);
    if (!resp.ok) {
      throw new Error("get plan by id: response is not ok");
    }
    const json = await resp.json();
    const etag = resp.headers.get("etag");
    if (!etag) {
      throw new Error("get plan by id: etag is empty");
    }
    return mapPlan(PlanSchema.parse(json), etag);
  },
  patch: async (
    planId: string,
    patch: PlanPatch,
    etag: string,
  ): Promise<string> => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/plans/${planId}`, {
      method: "PATCH",
      headers: {
        "if-match": etag,
      },
      body: JSON.stringify(patch),
    });
    if (!resp.ok) {
      throw new Error("patch plan: response is not ok");
    }
    const newEtag = resp.headers.get("etag");
    if (!newEtag) {
      throw new Error("patch plan: etag is empty");
    }
    return newEtag;
  },
  delete: async (planId: string): Promise<void> => {
    const resp = await fetch(`${CONFIG.gateway.baseURL}/plans/${planId}`, {
      method: "DELETE",
    });
    if (!resp.ok) {
      throw new Error("delete plan: response is not ok");
    }
  },
  getAllPlansInProject: async (projectId: string): Promise<Plan[]> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${projectId}/plans`,
    );
    if (!resp.ok) {
      throw new Error("get all plans in project: response is not ok");
    }
    const json = await resp.json();
    return PlansSchema.parse(json).map((plan) => mapPlan(plan, ""));
  },
};
