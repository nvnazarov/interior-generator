import moment from "moment";
import { useAppSelector } from "../../../app/hooks";
import { selectCanSync, selectProjectEditor } from "../slice";
import "./SyncAge.scss";

export function SyncAge() {
  const editor = useAppSelector(selectProjectEditor);
  const canSync = useAppSelector(selectCanSync);
  if (canSync) {
    const dtLastSaved = editor.dtLastSaved;
    return <div className="sync-age">{moment(dtLastSaved).fromNow()}</div>;
  } else {
    return <div className="sync-age">synced</div>;
  }
}
