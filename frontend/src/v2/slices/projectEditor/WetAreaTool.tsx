import { useCallback, useState } from "react";
import { useAppDispatch } from "../storeTypes";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { M, snapToGrid } from "./lib";
import { projectChanged } from "./slice";
import type { WetArea } from "../api/entities";
import { v4 as uuidv4 } from "uuid";
import { Plane } from "@react-three/drei";

const WET_AREA_PREVIEW_MATERIAL = new THREE.MeshStandardMaterial({
  color: "hotpink",
});

function WetAreaPreview({
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
      material={WET_AREA_PREVIEW_MATERIAL}
    />
  );
}

export function WetAreaTool() {
  const dispatch = useAppDispatch();
  const [isCreatingWetArea, setIsCreatingWetArea] = useState(false);
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
        setIsCreatingWetArea(true);
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
      if (isCreatingWetArea && isValidArea) {
        const area: WetArea = {
          id: uuidv4(),
          x: Math.min(areaStartPosition[0], areaEndPosition[0]),
          y: Math.min(areaStartPosition[1], areaEndPosition[1]),
          w: Math.abs(areaEndPosition[0] - areaStartPosition[0]),
          h: Math.abs(areaEndPosition[1] - areaStartPosition[1]),
        };
        dispatch(
          projectChanged({
            patch: { content: { wetAreas: { [area.id]: area } } },
            inversePatch: { content: { wetAreas: { [area.id]: null } } },
          }),
        );
      }
    } finally {
      setIsCreatingWetArea(false);
    }
  }, [isCreatingWetArea, areaStartPosition, areaEndPosition]);

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
      {isCreatingWetArea && (
        <WetAreaPreview
          startPosition={areaStartPosition}
          endPosition={areaEndPosition}
        />
      )}
    </>
  );
}
