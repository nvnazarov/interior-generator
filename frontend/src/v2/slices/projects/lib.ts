import { Config } from "../../shared/config";
import { UrlUtil } from "../../shared/util";

export async function exportAndDownloadProjectPdf(projectId: string, title: string) {
  const resp = await fetch(
    `${UrlUtil.noRightSlash(Config.gateway.baseUrl)}/api/projects/${projectId}/export/pdf`,
    {
      method: "POST",
      body: "{}",
      headers: { "Content-Type": "application/json" },
    },
  );
  if (!resp.ok) {
    throw new Error("error: export project pdf: response is not ok");
  }
  const blob = await resp.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${title}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}