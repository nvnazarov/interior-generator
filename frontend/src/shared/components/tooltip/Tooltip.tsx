import "./Tooltip.scss";
import {
  cloneElement,
  useState,
  type HTMLAttributes,
  type PointerEvent,
  type ReactElement,
  type ReactNode,
} from "react";
import { motion } from "motion/react";
import { createPortal } from "react-dom";

type TooltipProps = {
  children: ReactElement<HTMLAttributes<HTMLElement>>;
  content: ReactNode;
  position?: "top" | "bottom" | "left" | "right" | "auto";
};

export function Tooltip({
  children,
  content,
  position = "auto",
}: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const [anchor, setAnchor] = useState({
    top: 0,
    left: 0,
    width: 0,
    height: 0,
  });

  const child = cloneElement(children, {
    onPointerEnter: (e: PointerEvent<HTMLElement>) => {
      children.props.onPointerEnter?.(e);
      setVisible(true);
      const rect = e.currentTarget.getBoundingClientRect();
      setAnchor({
        top: rect.top,
        left: rect.left,
        width: e.currentTarget.clientWidth,
        height: e.currentTarget.clientHeight,
      });
    },
    onPointerLeave: (e: PointerEvent<HTMLElement>) => {
      children.props.onPointerLeave?.(e);
      setVisible(false);
    },
    onPointerDown: (e: PointerEvent<HTMLElement>) => {
      children.props.onPointerDown?.(e);
      setVisible(false);
    },
  } as HTMLAttributes<HTMLElement>);

  let left = 0;
  let top = 0;
  let transform = "translate(-50%)";
  let pLeft = "0";
  let pTop = "0";
  let pBottom = "auto";
  switch (position) {
    case "top":
      left = anchor.left + anchor.width / 2;
      top = anchor.top - 10;
      transform = "translate(-50%, -100%)";
      pTop = "auto";
      pBottom = "-6px";
      pLeft = "50%";
      break;
    case "auto":
    case "bottom":
      left = anchor.left + anchor.width / 2;
      top = anchor.top + anchor.height + 10;
      pTop = "0px";
      pLeft = "50%";
      break;
    case "left":
      left = anchor.left - anchor.width - 5;
      top = anchor.top - anchor.height / 2;
      transform = "translate(0, -100%)";
      pTop = "50%";
      pLeft = "0";
      break;
    case "right":
      left = anchor.left + anchor.width + 10;
      top = anchor.top - anchor.height / 2;
      transform = "translate(0, 50%)";
      pTop = "50%";
      pLeft = "0";
      break;
  }

  return (
    <>
      {child}
      {visible &&
        content &&
        createPortal(
          <div
            className="tooltip__container"
            style={{ top: top, left: left, transform: transform }}
          >
            <motion.div
              className="tooltip__tooltip"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5 }}
            >
              <div
                className="tooltip__pointer"
                style={{ top: pTop, bottom: pBottom, left: pLeft }}
              />
              {content}
            </motion.div>
          </div>,
          document.body,
        )}
    </>
  );
}
