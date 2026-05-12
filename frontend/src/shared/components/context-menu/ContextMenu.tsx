import {
  cloneElement,
  useRef,
  useState,
  type HTMLAttributes,
  type ReactElement,
  type ReactNode,
} from "react";
import { motion } from "motion/react";
import { createPortal } from "react-dom";

import "./ContextMenu.scss";

type ContextMenuAttributes = {
  children: ReactElement<HTMLAttributes<HTMLElement>>;
  content: ReactNode;
  position?: "top" | "bottom" | "left" | "right" | "auto";
};

export function ContextMenu({
  children,
  content,
  position = "auto",
}: ContextMenuAttributes) {
  const [visible, setVisible] = useState(false);
  const [anchor, setAnchor] = useState({
    top: 0,
    left: 0,
    width: 0,
    height: 0,
  });
  const menuRef = useRef<HTMLDivElement>(null);

  const child = cloneElement(children, {
    onFocus: (e) => {
      children.props.onFocus?.(e);
      const rect = e.currentTarget.getBoundingClientRect();
      setAnchor({
        top: rect.top,
        left: rect.left,
        width: e.currentTarget.clientWidth,
        height: e.currentTarget.clientHeight,
      });
      setVisible(true);
    },
    onBlur: (e) => {
      children.props.onBlur?.(e);
      if (menuRef.current && menuRef.current.contains(e.relatedTarget)) {
        return;
      }
      setVisible(false);
    },
  } as HTMLAttributes<HTMLElement>);

  let left = 0;
  let top = 0;
  let transform = "translate(0)";
  switch (position) {
    case "top":
      left = anchor.left;
      top = anchor.top - 20;
      transform = "translate(0, -100%)";
      break;
    case "auto":
    case "bottom":
      left = anchor.left;
      top = anchor.top + anchor.height + 20;
      break;
    case "left":
      left = anchor.left - anchor.width - 20;
      top = anchor.top;
      break;
    case "right":
      left = anchor.left + anchor.width + 20;
      top = anchor.top;
      break;
  }

  return (
    <>
      {child}
      {visible &&
        content &&
        createPortal(
          <div
            ref={menuRef}
            className="context-menu__container"
            style={{ top: top, left: left, transform: transform }}
          >
            <motion.div
              className="context-menu__menu"
              initial={{ rotateY: 90 }}
              animate={{ rotateY: 0 }}
            >
              {content}
            </motion.div>
          </div>,
          document.body,
        )}
    </>
  );
}
