import type { EventHandlers } from "@react-three/fiber";
import {
  cloneElement,
  useEffect,
  useRef,
  type ReactElement,
  type ReactNode,
} from "react";

import "./MeshHint.scss";
import { createRoot, type Root } from "react-dom/client";

export type CustomAttributes = {
  children: ReactElement<EventHandlers>;
  content: ReactNode;
};

export function MeshHint({ children, content }: CustomAttributes) {
  const element = useRef<HTMLDivElement>(null);
  const root = useRef<Root>(null);

  useEffect(() => {
    const div = document.createElement("div");
    element.current = div;
    element.current.classList.add("mesh-hint");
    document.body.appendChild(div);

    root.current = createRoot(element.current);
    root.current.render(content);

    const handleClick = () => {
      if (element.current) {
        element.current.style.display = "none";
      }
    };

    window.addEventListener("mousedown", handleClick);

    return () => {
      root.current?.unmount();
      document.body.removeChild(div);
      window.removeEventListener("mousedown", handleClick);
    };
  }, []);

  const child = cloneElement(children, {
    onPointerEnter: (e) => {
      children.props.onPointerEnter?.(e);
      if (element.current) {
        element.current.style.display = "inline-block";
        element.current.style.left = e.clientX + "px";
        element.current.style.top = e.clientY - 10 + "px";
      }
    },
    onPointerMove: (e) => {
      children.props.onPointerMove?.(e);
      if (element.current) {
        element.current.style.left = e.clientX + "px";
        element.current.style.top = e.clientY - 10 + "px";
      }
    },
    onPointerLeave: (e) => {
      children.props.onPointerLeave?.(e);
      if (element.current) {
        element.current.style.display = "none";
      }
    },
  });

  return child;
}
