import { useContext } from "react";
import { ContextMenuContext, type ContextMenu } from "../components";

export function useContextMenu(): ContextMenu {
  return useContext(ContextMenuContext);
}
