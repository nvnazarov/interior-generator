import { useCallback, useState } from "react";
import { useAppDispatch } from "../storeTypes";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { M, snapToGrid } from "./lib";
import { planChanged } from "./slice";
import type { FunctionalArea } from "../api/entities";
import { v4 as uuidv4 } from "uuid";
import { Plane } from "@react-three/drei";

const AREA_PREVIEW_MATERIAL = new THREE.MeshStandardMaterial({
  color: "hotpink",
});

function AreaPreview({
  startPosition,
  endPosition,
}: {
  startPosition: [number, number];
  endPosition: [number, number];
}) {
  const start = new THREE.Vector3(startPosition[0], 0, startPosition[1]);
  const end = new THREE.Vector3(endPosition[0], 0, endPosition[1]);
  const center = new THREE.Vector3()
    .subVectors(end, start)
    .multiplyScalar(0.5)
    .add(start);
  const sizeX = Math.abs(endPosition[0] - startPosition[0]);
  const sizeZ = Math.abs(endPosition[1] - startPosition[1]);
  return (
    <Plane
      args={[sizeX, sizeZ]}
      position={center}
      rotation={[-Math.PI / 2, 0, 0]}
      material={AREA_PREVIEW_MATERIAL}
    />
  );
}

export function AreaTool() {
  const dispatch = useAppDispatch();
  const [isCreatingArea, setIsCreatingArea] = useState(false);
  const [areaStartPosition, setAreaStartPosition] = useState<[number, number]>([
    0, 0,
  ]);
  const [areaEndPosition, setAreaEndPosition] = useState<[number, number]>([
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
        setIsCreatingArea(true);
        setAreaStartPosition(position);
        setAreaEndPosition(position);
      }
    },
    [getMousePosition],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      const position = getMousePosition(e);
      if (position) {
        setAreaEndPosition(position);
      }
    },
    [getMousePosition],
  );

  const handleMouseUp = useCallback(() => {
    try {
      const isValidArea =
        Math.abs(areaEndPosition[0] - areaStartPosition[0]) > 0 &&
        Math.abs(areaEndPosition[1] - areaStartPosition[1]) > 0;
      if (isCreatingArea && isValidArea) {
        const area: FunctionalArea = {
          id: uuidv4(),
          type: "",
          x: Math.min(areaStartPosition[0], areaEndPosition[0]),
          y: Math.min(areaStartPosition[1], areaEndPosition[1]),
          w: Math.abs(areaEndPosition[0] - areaStartPosition[0]),
          h: Math.abs(areaEndPosition[1] - areaStartPosition[1]),
        };
        dispatch(
          planChanged({
            patch: { content: { areas: { [area.id]: area } } },
            inversePatch: { content: { areas: { [area.id]: null } } },
          }),
        );
      }
    } finally {
      setIsCreatingArea(false);
    }
  }, [isCreatingArea, areaStartPosition, areaEndPosition]);

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
      {isCreatingArea && (
        <AreaPreview
          startPosition={areaStartPosition}
          endPosition={areaEndPosition}
        />
      )}
    </>
  );
}
