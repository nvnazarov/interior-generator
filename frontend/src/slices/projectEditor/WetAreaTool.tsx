import { useCallback, useMemo, useState } from "react";
import { useAppDispatch } from "../storeTypes";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { CM, M, snapToGrid } from "./lib";
import { projectChanged } from "./slice";
import type { FunctionalArea, WetArea } from "../api/entities";
import { v4 as uuidv4 } from "uuid";

function AreaPreview({
  points,
  position,
}: {
  points: { x: number; y: number }[];
  position: { x: number; y: number } | null;
}) {
  const shape = useMemo(() => {
    const shape = new THREE.Shape();
    if (points.length > 2) {
      shape.moveTo(points[0]!.x, points[0]!.y);
      for (let i = 1; i < points.length; i++) {
        shape.lineTo(points[i]!.x, points[i]!.y);
      }
      shape.closePath();
    }
    return shape;
  }, [points]);

  const addShape = useMemo(() => {
    const shape = new THREE.Shape();
    if (points.length >= 2 && position) {
      shape.moveTo(points[0]!.x, points[0]!.y);
      shape.lineTo(points[points.length - 1]!.x, points[points.length - 1]!.y);
      shape.lineTo(position.x, position.y);
      shape.closePath();
    }
    return shape;
  }, [points, position]);

  return (
    <>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <shapeGeometry args={[shape]} />
        <meshStandardMaterial color="hotpink" side={THREE.DoubleSide} />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <shapeGeometry args={[addShape]} />
        <meshStandardMaterial color="green" side={THREE.DoubleSide} />
      </mesh>
    </>
  );
}

export function WetAreaTool() {
  const dispatch = useAppDispatch();
  const [position, setPosition] = useState<{ x: number; y: number } | null>(
    null,
  );
  const [points, setPoints] = useState<{ x: number; y: number }[]>([]);
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
      if (
        position &&
        !points.find(
          (point) => point.x === position[0] && point.y === position[1],
        )
      ) {
        setPoints([...points, { x: position[0], y: position[1] }]);
      }
    },
    [getMousePosition, points],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      const position = getMousePosition(e);
      if (position) {
        setPosition({ x: position[0], y: position[1] });
      }
    },
    [getMousePosition],
  );

  const handleStartPointClick = useCallback(() => {
    const area: WetArea = {
      id: uuidv4(),
      points: points,
    };
    dispatch(
      projectChanged({
        patch: { content: { wetAreas: { [area.id]: area } } },
        inversePatch: { content: { wetAreas: { [area.id]: null } } },
      }),
    );
    setPoints([]);
  }, [points]);

  return (
    <>
      <mesh
        position={[0, 0, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerDown={handleMouseDown}
        onPointerMove={handleMouseMove}
      >
        <planeGeometry args={[1000 * M, 1000 * M]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      <AreaPreview points={points} position={position} />
      {points.length > 0 && (
        <mesh
          position={[points[0]!.x, 3.5 * M, points[0]!.y]}
          onClick={handleStartPointClick}
        >
          <sphereGeometry args={[10 * CM, 32, 32]} />
          <meshStandardMaterial color="green" />
        </mesh>
      )}
      {position && (
        <mesh position={[position.x, 3.5 * M, position.y]}>
          <sphereGeometry args={[10 * CM, 32, 32]} />
          <meshStandardMaterial color="red" />
        </mesh>
      )}
    </>
  );
}
