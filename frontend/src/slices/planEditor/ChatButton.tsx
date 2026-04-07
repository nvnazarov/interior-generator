import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { chatSwitched, selectIsChatOpen } from "./slice";

export function ChatButton() {
  const dispatch = useAppDispatch();
  const isOpen = useAppSelector(selectIsChatOpen);

  const handleClick = useCallback(() => {
    dispatch(chatSwitched());
  }, []);

  return <Button icon="magic.png" onClick={handleClick} active={isOpen} />;
}
