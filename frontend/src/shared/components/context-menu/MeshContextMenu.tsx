import type { EventHandlers } from "@react-three/fiber";
import {
  cloneElement,
  useEffect,
  useRef,
  type ReactElement,
  type ReactNode,
} from "react";
import { motion } from "motion/react";
import { createRoot, type Root } from "react-dom/client";

import "./ContextMenu.scss";

type ContextMenuAttributes = {
  children: ReactElement<EventHandlers>;
  content: ReactNode;
};

export function MeshContextMenu({ children, content }: ContextMenuAttributes) {
  const element = useRef<HTMLDivElement>(null);
  const root = useRef<Root>(null);

  useEffect(() => {
    const div = document.createElement("div");
    element.current = div;
    element.current.classList.add("mesh-hint");
    document.body.appendChild(div);

    root.current = createRoot(element.current);
    root.current.render(
      <div className="context-menu__container">
        <motion.div
          className="context-menu__menu"
          initial={{ rotateY: 90 }}
          animate={{ rotateY: 0 }}
        >
          {content}
        </motion.div>
      </div>,
    );

    return () => {
      root.current?.unmount();
      document.body.removeChild(div);
    };
  }, []);

  const child = cloneElement(children, {
    onContextMenu: (e) => {
      console.log("123");
      children.props.onContextMenu?.(e);
      if (element.current) {
        element.current.style.display = "inline-block";
        element.current.style.left = e.clientX + "px";
        element.current.style.top = e.clientY - 10 + "px";
      }
    },
  });

  return child;
}
