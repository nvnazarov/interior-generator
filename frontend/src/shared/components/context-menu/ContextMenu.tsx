import {
  cloneElement,
  useEffect,
  useRef,
  useState,
  type HTMLAttributes,
  type ReactElement,
  type ReactNode,
} from "react";
import { motion } from "motion/react";

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

  useEffect(() => {
    if (!visible) {
      return;
    }
    const handleMouseDown = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as any)) {
        setVisible(false);
      }
    };
    window.addEventListener("mousedown", handleMouseDown);
    return () => {
      window.removeEventListener("mousedown", handleMouseDown);
    };
  }, [visible]);

  const child = cloneElement(children, {
    onClick: (e) => {
      children.props.onClick?.(e);
      setAnchor({
        top: e.currentTarget.offsetTop,
        left: e.currentTarget.offsetLeft,
        width: e.currentTarget.clientWidth,
        height: e.currentTarget.clientHeight,
      });
      setVisible(true);
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
      {visible && content && (
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
        </div>
      )}
    </>
  );
}
