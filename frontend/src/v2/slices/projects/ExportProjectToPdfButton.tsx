import { useCallback } from "react";
import { exportAndDownloadProjectPdf } from "./lib";
import { Button } from "../../shared/components";

export function ExportProjectToPdfButton({ projectId }: { projectId: string }) {
  const handleClick = useCallback(() => {
    exportAndDownloadProjectPdf(projectId, `project-${projectId}`);
  }, [projectId]);

  return <Button onClick={handleClick} icon="pdf.png" />;
}
