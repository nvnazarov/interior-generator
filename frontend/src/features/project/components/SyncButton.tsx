import { useState } from "react";
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { selectCanSync, syncProjectEditorChanges } from "../slice";
import { Icon } from "./Icon";
import "./SyncButton.scss";

export function SyncButton() {
  const dispatch = useAppDispatch();
  const canSync = useAppSelector(selectCanSync);
  const [isSyncing, setIsSyncing] = useState(false);

  function handleClick() {
    if (isSyncing) return;
    setIsSyncing(true);
    dispatch(syncProjectEditorChanges()).finally(() => setIsSyncing(false));
  }

  return (
    <button
      onClick={handleClick}
      className={
        canSync && !isSyncing ? "sync-button" : "sync-button__disabled"
      }
    >
      <Icon src="icons/sync.png" />
    </button>
  );
}
