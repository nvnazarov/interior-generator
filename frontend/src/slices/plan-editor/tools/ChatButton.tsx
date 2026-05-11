import { useCallback } from "react";
import { Toggle } from "../../../shared/components/toggle/Toggle";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { chatSwitched, selectIsChatOpen } from "../slice";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function ChatButton() {
  const dispatch = useAppDispatch();
  const isOpen = useAppSelector(selectIsChatOpen);

  const handleChange = useCallback(() => {
    dispatch(chatSwitched());
  }, []);

  return (
    <Tooltip
      content={
        <p style={{ fontWeight: 400 }}>
          Chat with <b>AI-assistant</b>. You can ask assistant to generate
          interior designs or modify your existing design.
        </p>
      }
    >
      <Toggle icon="magic.png" onChange={handleChange} checked={isOpen} />
    </Tooltip>
  );
}
