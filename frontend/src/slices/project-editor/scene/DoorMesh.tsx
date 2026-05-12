import * as THREE from "three";
import type { Door, Wall } from "../../api/entities";
import { CM, M, WALL_WIDTH } from "../lib";
import { useCallback, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { useAppDispatch } from "../../storeTypes";
import { projectChanged } from "../slice";
import { ContextMenuOption, MeshMenu } from "../../../shared/components";

export function DoorMesh({
  door,
  wall,
}: {
  door: Door & { id: string };
  wall: Wall;
}) {
  const dispatch = useAppDispatch();
  const [hovered, setHovered] = useState(false);

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

  const handleDelete = useCallback(() => {
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
  }, [door]);

  const handlePointerEnter = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(true);
    e.stopPropagation();
  }, []);

  const handlePointerOut = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(false);
    e.stopPropagation();
  }, []);

  return (
    <MeshMenu
      hint={
        <>
          Door
          <br />
          <br />
          <b>Width:</b> {door.w / M} m<br />
          <b>Height:</b> {door.h / M} m
        </>
      }
      menu={
        <>
          <ContextMenuOption text="Delete door" onClick={handleDelete} />
        </>
      }
    >
      <mesh
        position={[center.x, door.h / 2, center.z]}
        rotation={[0, -angle, 0]}
        onPointerEnter={handlePointerEnter}
        onPointerOut={handlePointerOut}
      >
        <boxGeometry args={[length, door.h, WALL_WIDTH + 4 * CM]} />
        <meshStandardMaterial color={hovered ? "hotpink" : "brown"} />
      </mesh>
    </MeshMenu>
  );
}
