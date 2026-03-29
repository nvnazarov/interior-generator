import { useCallback, useState } from "react";
import { CM, M, snapToGrid } from "./lib";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { useAppDispatch } from "../storeTypes";
import { v4 as uuidv4 } from "uuid";
import type { Wall } from "../api/entities";
import { projectChanged } from "./slice";

function WallPreview({
  startPosition,
  endPosition,
}: {
  startPosition: [number, number];
  endPosition: [number, number];
}) {
  const start = new THREE.Vector3(startPosition[0], 0, startPosition[1]);
  const end = new THREE.Vector3(endPosition[0], 0, endPosition[1]);
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start).normalize();
  const angle = Math.atan2(direction.z, direction.x);

  return (
    <mesh
      position={[center.x, (3 * M) / 2, center.z]}
      rotation={[0, -angle, 0]}
    >
      <boxGeometry args={[length, 3 * M, 20 * CM]} />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}

export function WallTool() {
  const dispatch = useAppDispatch();
  const [isCreatingWall, setIsCreatingWall] = useState(false);
  const [wallStartPosition, setWallStartPosition] = useState<[number, number]>([
    0, 0,
  ]);
  const [wallEndPosition, setWallEndPosition] = useState<[number, number]>([
    0, 0,
  ]);
  const { camera, raycaster } = useThree();

  const getMousePosition = useCallback(
    (e: React.MouseEvent): [number, number] | null => {
      const mouse = new THREE.Vector2(
        (e.clientX / window.innerWidth) * 2 - 1,
        -(e.clientY / window.innerHeight) * 2 + 1,
      );
      raycaster.setFromCamera(mouse, camera);
      const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
      const target = new THREE.Vector3();
      if (raycaster.ray.intersectPlane(plane, target)) {
        return snapToGrid([target.x, target.z], M);
      }
      return null;
    },
    [camera, raycaster],
  );

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.button !== 0) {
        return;
      }
      const position = getMousePosition(e);
      if (position) {
        setIsCreatingWall(true);
        setWallStartPosition(position);
        setWallEndPosition(position);
      }
    },
    [getMousePosition],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      const position = getMousePosition(e);
      if (position) {
        setWallEndPosition(position);
      }
    },
    [getMousePosition],
  );

  const handleMouseUp = useCallback(() => {
    try {
      const isValidWall =
        Math.hypot(
          wallEndPosition[0] - wallStartPosition[0],
          wallEndPosition[1] - wallStartPosition[1],
        ) >
        20 * CM;
      if (isCreatingWall && isValidWall) {
        const wall: Wall = {
          id: uuidv4(),
          x1: wallStartPosition[0],
          y1: wallStartPosition[1],
          x2: wallEndPosition[0],
          y2: wallEndPosition[1],
        };
        dispatch(
          projectChanged({
            patch: { content: { walls: { [wall.id]: wall } } },
            inversePatch: { content: { walls: { [wall.id]: null } } },
          }),
        );
      }
    } finally {
      setIsCreatingWall(false);
    }
  }, [isCreatingWall, wallStartPosition, wallEndPosition]);

  return (
    <>
      <mesh
        position={[0, 0, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerDown={handleMouseDown}
        onPointerMove={handleMouseMove}
        onPointerUp={handleMouseUp}
      >
        <planeGeometry args={[1000 * M, 1000 * M]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      {isCreatingWall && (
        <WallPreview
          startPosition={wallStartPosition}
          endPosition={wallEndPosition}
        />
      )}
    </>
  );
}
