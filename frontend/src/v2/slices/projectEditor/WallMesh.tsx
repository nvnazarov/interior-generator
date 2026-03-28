import type { Door, Wall, Window } from "../api/entities";
import { CM, M, snapToGrid } from "./lib";
import * as THREE from "three";
import { projectChanged, selectProjectEditorTool } from "./slice";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { useCallback, useMemo, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { v4 as uuidv4 } from "uuid";

function WindowPreview({
  startPoint,
  endPoint,
  wall,
}: {
  startPoint: [number, number];
  endPoint: [number, number];
  wall: Wall;
}) {
  const wallStart = new THREE.Vector3(wall.x1, 0, wall.y1);
  const wallEnd = new THREE.Vector3(wall.x2, 0, wall.y2);
  const direction = new THREE.Vector3()
    .subVectors(wallEnd, wallStart)
    .normalize();
  const start = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(startPoint[0]));
  const end = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(endPoint[0]));
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const angle = Math.atan2(direction.z, direction.x);

  return (
    <mesh
      position={[
        center.x,
        Math.min(startPoint[1], endPoint[1]) +
          Math.abs(endPoint[1] - startPoint[1]) / 2,
        center.z,
      ]}
      rotation={[0, -angle, 0]}
    >
      <boxGeometry
        args={[length, Math.abs(endPoint[1] - startPoint[1]), 24 * CM]}
      />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}

function DoorPreview({
  startPoint,
  endPoint,
  wall,
}: {
  startPoint: [number, number];
  endPoint: [number, number];
  wall: Wall;
}) {
  const wallStart = new THREE.Vector3(wall.x1, 0, wall.y1);
  const wallEnd = new THREE.Vector3(wall.x2, 0, wall.y2);
  const direction = new THREE.Vector3()
    .subVectors(wallEnd, wallStart)
    .normalize();
  const start = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(startPoint[0]));
  const end = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(endPoint[0]));
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const angle = Math.atan2(direction.z, direction.x);

  return (
    <mesh
      position={[center.x, Math.max(endPoint[1], startPoint[1]) / 2, center.z]}
      rotation={[0, -angle, 0]}
    >
      <boxGeometry
        args={[length, Math.max(endPoint[1], startPoint[1]), 24 * CM]}
      />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}

export function WallMesh({ wall }: { wall: Wall }) {
  const dispatch = useAppDispatch();
  const tool = useAppSelector(selectProjectEditorTool);
  const [startPoint, setStartPoint] = useState<[number, number]>([0, 0]);
  const [endPoint, setEndPoint] = useState<[number, number]>([0, 0]);
  const [isCreatingWindowOrDoor, setIsCreatingWindowOrDoor] = useState(false);

  const start = new THREE.Vector3(wall.x1, 0, wall.y1);
  const end = new THREE.Vector3(wall.x2, 0, wall.y2);
  const length = start.distanceTo(end) + 20 * CM;
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start).normalize();
  const angle = Math.atan2(direction.z, direction.x);

  const worldToWallMatrix = useMemo(() => {
    const matrix = new THREE.Matrix4();
    const localX = direction.clone();
    const localY = new THREE.Vector3(0, 1, 0);
    const localZ = new THREE.Vector3().crossVectors(localX, localY).normalize();
    matrix.makeBasis(localX, localY, localZ);
    matrix.setPosition(start);
    return matrix;
  }, [start, direction]);

  const getWallLocalPoint = useCallback(
    (worldPoint: THREE.Vector3): [number, number] => {
      const localPoint = worldPoint
        .clone()
        .applyMatrix4(worldToWallMatrix.clone().invert());
      return snapToGrid([localPoint.x, localPoint.y], 20 * CM);
    },
    [worldToWallMatrix],
  );

  const handlePointerDown = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      if (["window", "door"].includes(tool) && e.button === 0) {
        setIsCreatingWindowOrDoor(true);
        const point = getWallLocalPoint(e.point);
        setStartPoint(point);
        setEndPoint(point);
        e.stopPropagation();
      }
    },
    [tool],
  );

  const handlePointerMove = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      if (["window", "door"].includes(tool)) {
        setEndPoint(getWallLocalPoint(e.point));
      }
    },
    [tool],
  );

  const handlePointerUp = useCallback(() => {
    if (!isCreatingWindowOrDoor) {
      return;
    }
    try {
      if (!startPoint || !endPoint) return;
      const x1 = Math.min(startPoint[0], endPoint[0]);
      const x2 = Math.max(startPoint[0], endPoint[0]);
      const y1 = Math.min(startPoint[1], endPoint[1]);
      const y2 = Math.max(startPoint[1], endPoint[1]);
      if (tool === "window") {
        const window: Window = {
          id: uuidv4(),
          wallId: wall.id,
          x: x1,
          y: y1,
          w: x2 - x1,
          h: y2 - y1,
        };
        dispatch(
          projectChanged({
            patch: {
              content: {
                windows: {
                  [window.id]: window,
                },
              },
            },
            inversePatch: {
              content: {
                windows: {
                  [window.id]: null,
                },
              },
            },
          }),
        );
      }
      if (tool === "door") {
        const door: Door = {
          id: uuidv4(),
          wallId: wall.id,
          x: x1,
          w: x2 - x1,
          h: y2,
        };
        dispatch(
          projectChanged({
            patch: {
              content: {
                doors: {
                  [door.id]: door,
                },
              },
            },
            inversePatch: {
              content: {
                doors: {
                  [door.id]: null,
                },
              },
            },
          }),
        );
      }
    } finally {
      setIsCreatingWindowOrDoor(false);
    }
  }, [tool, wall.id, startPoint, endPoint, isCreatingWindowOrDoor]);

  const handlePointerLeave = useCallback(() => {
    setIsCreatingWindowOrDoor(false);
  }, []);

  return (
    <>
      <mesh
        position={[center.x, (3 * M) / 2, center.z]}
        rotation={[0, -angle, 0]}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerLeave}
      >
        <boxGeometry args={[length, 3 * M, 20 * CM]} />
        <meshStandardMaterial color="white" />
      </mesh>
      {isCreatingWindowOrDoor &&
        (tool === "window" ? (
          <WindowPreview
            startPoint={startPoint}
            endPoint={endPoint}
            wall={wall}
          />
        ) : (
          <DoorPreview
            startPoint={startPoint}
            endPoint={endPoint}
            wall={wall}
          />
        ))}
    </>
  );
}
