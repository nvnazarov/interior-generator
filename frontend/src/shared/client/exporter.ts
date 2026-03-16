import { CONFIG } from "../config";

export const ExporterClient = {
  exportProjectPDF: async (projectId: string): Promise<Blob> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/projects/${projectId}/export/pdf`,
      {
        method: "POST",
        body: "{}",
        headers: { "Content-Type": "application/json" },
      },
    );
    if (!resp.ok) {
      throw new Error("export project pdf: response is not ok");
    }
    return await resp.blob();
  },
  exportPlanDXF: async (planId: string): Promise<Blob> => {
    const resp = await fetch(
      `${CONFIG.gateway.baseURL}/plans/${planId}/export/dxf`,
      {
        method: "POST",
        body: "{}",
        headers: { "Content-Type": "application/json" },
      },
    );
    if (!resp.ok) {
      throw new Error("export plan dxf: response is not ok");
    }
    return await resp.blob();
  },
};
