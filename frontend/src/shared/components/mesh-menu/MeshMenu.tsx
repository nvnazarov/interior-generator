import type { EventHandlers } from "@react-three/fiber";
import {
  cloneElement,
  useEffect,
  useRef,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";

import "./MeshMenu.scss";
import { Html } from "@react-three/drei";
import { Vector3 } from "three";
import { motion } from "motion/react";

export type CustomAttributes = {
  children: ReactElement<EventHandlers>;
  menu?: ReactNode;
  hint?: ReactNode;
};

export function MeshMenu({ children, menu, hint }: CustomAttributes) {
  const [hintVisible, setHintVisible] = useState(false);
  const [menuVisible, setMenuVisible] = useState(false);
  const [position, setPosition] = useState<Vector3>(new Vector3(0, 0, 0));
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuVisible) {
      return;
    }
    const handleMouseDown = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as any)) {
        setMenuVisible(false);
      }
    };
    window.addEventListener("mousedown", handleMouseDown);
    return () => {
      window.removeEventListener("mousedown", handleMouseDown);
    };
  }, [menuVisible]);

  const child = cloneElement(children, {
    onPointerEnter: (e) => {
      children.props.onPointerEnter?.(e);
      if (!menuVisible) {
        setHintVisible(true);
        setPosition(e.point);
      }
      e.stopPropagation();
    },
    onPointerMove: (e) => {
      children.props.onPointerMove?.(e);
      if (hintVisible && !menuVisible) {
        setPosition(e.point);
      }
      e.stopPropagation();
    },
    onPointerLeave: (e) => {
      children.props.onPointerLeave?.(e);
      setHintVisible(false);
      e.stopPropagation();
    },
    onContextMenu: (e) => {
      children.props.onContextMenu?.(e);
      if (menu) {
        setPosition(e.point);
        setHintVisible(false);
        setMenuVisible(true);
      }
      e.stopPropagation();
    },
  });

  return (
    <>
      {child}
      {hint && hintVisible && !menuVisible && (
        <Html position={position} center style={{ pointerEvents: "none" }}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mesh-menu__hint"
          >
            {hint}
          </motion.div>
        </Html>
      )}
      {menu && menuVisible && (
        <Html position={position} center style={{ pointerEvents: "none" }}>
          {
            <motion.div
              ref={menuRef}
              className="mesh-menu__menu"
              initial={{ rotateY: 90 }}
              animate={{ rotateY: 0 }}
            >
              {menu}
            </motion.div>
          }
        </Html>
      )}
    </>
  );
}
