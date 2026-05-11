import * as THREE from "three";
import type { Wall, Window } from "../../api/entities";
import { CM } from "../lib";
import { useCallback, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { useContextMenu } from "../../../shared/hooks/contextMenu";
import { useAppDispatch } from "../../storeTypes";
import { projectChanged } from "../slice";
import { useTranslation } from "react-i18next";

export function WindowMesh({
  window,
  wall,
}: {
  window: Window & { id: string };
  wall: Wall;
}) {
  const dispatch = useAppDispatch();
  const menu = useContextMenu();
  const [hovered, setHovered] = useState(false);
  const { t } = useTranslation();

  const wallStart = new THREE.Vector3(wall.x1, 0, wall.y1);
  const wallEnd = new THREE.Vector3(wall.x2, 0, wall.y2);
  const direction = new THREE.Vector3()
    .subVectors(wallEnd, wallStart)
    .normalize();
  const start = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(window.x));
  const end = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(window.x + window.w));
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const angle = Math.atan2(direction.z, direction.x);

  const handleContextMenu = useCallback((e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    menu.show({
      title: t("ProjectEditor.WindowMesh.Name", "Window"),
      x: e.clientX,
      y: e.clientY,
      items: [
        {
          name: t("ProjectEditor.WindowMesh.DeleteOption.Title", "Delete"),
          onClick: () => {
            dispatch(
              projectChanged({
                patch: {
                  content: {
                    windows: {
                      [window.id]: null,
                    },
                  },
                },
                inversePatch: {
                  content: {
                    windows: {
                      [window.id]: window,
                    },
                  },
                },
              }),
            );
          },
        },
      ],
    });
  }, []);

  const handlePointerEnter = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(true);
    e.stopPropagation();
  }, []);

  const handlePointerOut = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(false);
    e.stopPropagation();
  }, []);

  return (
    <mesh
      position={[center.x, window.y + window.h / 2, center.z]}
      rotation={[0, -angle, 0]}
      onContextMenu={handleContextMenu}
      onPointerEnter={handlePointerEnter}
      onPointerOut={handlePointerOut}
    >
      <boxGeometry args={[length, window.h, 24 * CM]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "blue"} />
    </mesh>
  );
}
