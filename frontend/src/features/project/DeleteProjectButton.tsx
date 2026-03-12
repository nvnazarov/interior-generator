import { useAppDispatch } from "../../app/hooks";
import { useState } from "react";
import { deleteProject } from "./projectSlice";

export interface Props {
  id: string;
}

export function DeleteProjectButton({ id }: Props) {
  const dispatch = useAppDispatch();
  const [busy, setBusy] = useState(false);

  const handleClick = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();
    try {
      setBusy(true);
      await dispatch(deleteProject(id)).unwrap();
    } catch (e) {
      // TODO
    } finally {
      setBusy(false);
    }
  };

  return (
    <button onClick={(e) => handleClick(e)} disabled={busy}>
      Delete
    </button>
  );
}
