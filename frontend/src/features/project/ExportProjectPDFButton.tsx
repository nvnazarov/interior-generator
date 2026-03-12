import { useState } from "react";
import { useAppDispatch } from "../../app/hooks";
import { exportProjectPDF } from "./projectSlice";

export interface Props {
  id: string;
}

export function ExportProjectPDFButton({ id }: Props) {
  const dispatch = useAppDispatch();
  const [busy, setBusy] = useState(false);

  const handleClick = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();
    try {
      setBusy(true);
      await dispatch(exportProjectPDF(id)).unwrap();
    } catch (e) {
      // TODO
    } finally {
      setBusy(false);
    }
  };

  return (
    <button onClick={(e) => handleClick(e)} disabled={busy}>
      Export PDF
    </button>
  );
}
