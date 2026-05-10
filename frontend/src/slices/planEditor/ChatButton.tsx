import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { chatSwitched, selectIsChatOpen } from "./slice";
import { Tooltip } from "../../shared/components/tooltip/Tooltip";

export function ChatButton() {
  const dispatch = useAppDispatch();
  const isOpen = useAppSelector(selectIsChatOpen);

  const handleClick = useCallback(() => {
    dispatch(chatSwitched());
  }, []);

  return (
    <Tooltip
      content={
        <>
          Open chat with your <b>AI assistant</b>
        </>
      }
    >
      <Button icon="magic.png" onClick={handleClick} active={isOpen} />
    </Tooltip>
  );
}
