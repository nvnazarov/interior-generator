import type { EventHandlers } from "@react-three/fiber";
import { useEffect, type ReactNode } from "react";
import { createPortal } from "react-dom";

export type CustomAttributes = {
  children: ReactNode & EventHandlers;
  content: ReactNode;
};

export function MeshHint({ children, content }: CustomAttributes) {
  // useEffect(() => {
  //   const element = createPortal(<div>123</div>, document.body);
  //   return () => {
  //     document.body.removeChild(element);
  //   };
  // }, [])

  return (
    <>
      {children}
      {/* {createPortal(<div>123</div>, document.body)} */}
    </>
  );
}
