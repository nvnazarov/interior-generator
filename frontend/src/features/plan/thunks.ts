import { createAsyncThunk } from "@reduxjs/toolkit";
import { Client } from "../../shared/client";
import type { PlanPatch } from "./entities";

export const fetchAllPlansInProject = createAsyncThunk(
  "plans/fetchAllPlansInProject",
  Client.plans.getAllPlansInProject,
);

export const fetchPlan = createAsyncThunk(
  "plans/fetchPlanById",
  Client.plans.getById,
);

export const createPlan = createAsyncThunk(
  "plans/createPlan",
  Client.plans.create,
);

export const deletePlan = createAsyncThunk(
  "plans/deletePlan",
  Client.plans.delete,
);

export const exportPlanDXF = createAsyncThunk(
  "plans/exportPlanDXF",
  async (planId: string) => {
    const blob = await Client.exporter.exportPlanDXF(planId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `plan-${planId}.dxf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
);

export const patchPlan = createAsyncThunk(
  "plans/patchPlan",
  async ({
    planId,
    patch,
    etag,
  }: {
    planId: string;
    patch: PlanPatch;
    etag: string;
  }) => {
    const newEtag = await Client.plans.patch(planId, patch, etag);
    return newEtag;
  },
);
