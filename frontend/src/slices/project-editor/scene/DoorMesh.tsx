import * as THREE from "three";
import type { Door, Wall } from "../../api/entities";
import { CM } from "../lib";
import { useCallback, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { useContextMenu } from "../../../shared/hooks/contextMenu";
import { useAppDispatch } from "../../storeTypes";
import { projectChanged } from "../slice";
import { useTranslation } from "react-i18next";
import { MeshHint } from "../../../shared/components/mesh-hint/MeshHint";

export function DoorMesh({
  door,
  wall,
}: {
  door: Door & { id: string };
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
  const start = wallStart.clone().add(direction.clone().multiplyScalar(door.x));
  const end = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(door.x + door.w));
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const angle = Math.atan2(direction.z, direction.x);

  const handleContextMenu = useCallback((e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    menu.show({
      title: t("ProjectEditor.DoorMesh.Name", "Door"),
      x: e.clientX,
      y: e.clientY,
      items: [
        {
          name: t("ProjectEditor.DoorMesh.DeleteOption.Title", "Delete"),
          onClick: () => {
            dispatch(
              projectChanged({
                patch: {
                  content: {
                    doors: {
                      [door.id]: null,
                    },
                  },
                },
                inversePatch: {
                  content: {
                    doors: {
                      [door.id]: door,
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
    <MeshHint content="123">
      <mesh
        position={[center.x, door.h / 2, center.z]}
        rotation={[0, -angle, 0]}
        onContextMenu={handleContextMenu}
        onPointerEnter={handlePointerEnter}
        onPointerOut={handlePointerOut}
      >
        <boxGeometry args={[length, door.h, 24 * CM]} />
        <meshStandardMaterial color={hovered ? "hotpink" : "brown"} />
      </mesh>
    </MeshHint>
  );
}
