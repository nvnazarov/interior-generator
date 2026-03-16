import * as THREE from "three";
import React, { useState } from "react";
import "./ProjectEditor.scss";
import { Canvas, useThree, type ThreeEvent } from "@react-three/fiber";
import { type Wall } from "../project";
import { selectProjectEditor } from "../slice";
import { useAppSelector } from "../../../app/hooks";
import {
  CameraControls,
  OrbitControls,
  OrthographicCamera,
  CameraControlsImpl,
} from "@react-three/drei";

const { ACTION } = CameraControlsImpl;
const WALL_HEIGHT = 300;
const WALL_DEPTH = 20;

export interface Props {
  id: string;
}

export function WallObject({ wall }: { wall: Wall }) {
  const [hovered, hover] = useState(false);

  const start = new THREE.Vector3(wall.x1, 0, wall.y1);
  const end = new THREE.Vector3(wall.x2, 0, wall.y2);
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start).normalize();
  const angle = Math.atan2(direction.z, direction.x);

  function handlePointerOver(e: ThreeEvent<PointerEvent>) {
    e.stopPropagation();
    hover(true);
  }

  function handlePointerOut(e: ThreeEvent<PointerEvent>) {
    hover(false);
  }

  return (
    <mesh
      position={[center.x, WALL_HEIGHT / 2, center.z]}
      rotation={[0, -angle, 0]}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
    >
      <boxGeometry args={[length, WALL_HEIGHT, WALL_DEPTH]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "white"} />
    </mesh>
  );
}

export function Walls() {
  const editor = useAppSelector(selectProjectEditor);
  const isMode2D = editor.viewMode === "2d";
  const isWallTool = editor.activeTool === "wall";

  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null);
  const [previewEndPoint, setPreviewEndPoint] = useState<
    [number, number] | null
  >(null);
  const [walls, setWalls] = useState<Wall[]>([
    { id: "1", x1: 0, y1: 0, x2: 200, y2: 200 },
    { id: "2", x1: 200, y1: 200, x2: 400, y2: 0 },
  ]);

  const { camera, raycaster } = useThree();

  function getMousePosition(e: React.MouseEvent): [number, number] | null {
    const mouse = new THREE.Vector2(
      (e.clientX / window.innerWidth) * 2 - 1,
      -(e.clientY / window.innerHeight) * 2 + 1,
    );
    raycaster.setFromCamera(mouse, camera);
    const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const target = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(plane, target)) {
      return [target.x, target.z];
    }
    return null;
  }

  function handleMouseDown(e: React.MouseEvent) {
    if (!isMode2D || !isWallTool || e.button !== 0) return;
    const pos = getMousePosition(e);
    if (pos) {
      setIsDrawing(true);
      setStartPoint(pos);
      setPreviewEndPoint(pos);
    }
  }

  function handleMouseMove(e: React.MouseEvent) {
    if (!isMode2D || !isWallTool || !isDrawing || !startPoint) return;
    const pos = getMousePosition(e);
    if (pos) {
      setPreviewEndPoint(pos);
    }
  }

  function handleMouseUp(e: React.MouseEvent) {
    if (!isMode2D || !isWallTool || !isDrawing || !startPoint || e.button !== 0)
      return;
    const endPoint = previewEndPoint;
    if (endPoint && startPoint) {
      const dx = endPoint[0] - startPoint[0];
      const dy = endPoint[1] - startPoint[1];
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
        const newWall = {
          id: Math.random().toString(36).substr(2, 9),
          x1: startPoint[0],
          y1: startPoint[1],
          x2: endPoint[0],
          y2: endPoint[1],
        };

        setWalls((prev) => [...prev, newWall]);
      }
    }
    setIsDrawing(false);
    setStartPoint(null);
    setPreviewEndPoint(null);
  }

  return (
    <>
      <mesh
        position={[0, 0, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerDown={handleMouseDown}
        onPointerMove={handleMouseMove}
        onPointerUp={handleMouseUp}
        onPointerLeave={() => setIsDrawing(false)}
      >
        <planeGeometry args={[100000, 100000]} />
        {/* <meshBasicMaterial color="white" /> */}
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      {walls.map((wall) => (
        <WallObject key={wall.id} wall={wall} />
      ))}
      {isDrawing && startPoint && previewEndPoint && (
        <WallObject
          wall={{
            id: "preview",
            x1: startPoint[0],
            y1: startPoint[1],
            x2: previewEndPoint[0],
            y2: previewEndPoint[1],
          }}
        />
      )}
    </>
  );
}

export function ProjectEditor({ id }: { id: string }) {
  const editor = useAppSelector(selectProjectEditor);
  const isMode2D = editor.viewMode === "2d";

  return (
    <Canvas>
      <ambientLight intensity={1} />
      <directionalLight position={[5, 5, 5]} />
      <OrthographicCamera
        position={[0, 600, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        far={10000}
        near={0.1}
        makeDefault
      />
      {isMode2D ? (
        <OrbitControls maxPolarAngle={0} makeDefault />
      ) : (
        <CameraControls
          mouseButtons={{
            left: ACTION.ROTATE,
            middle: ACTION.ROTATE,
            wheel: ACTION.NONE,
            right: ACTION.TRUCK,
          }}
          makeDefault
        />
      )}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[5]} />
        <meshStandardMaterial color={"green"} />
      </mesh>
      <Walls />
    </Canvas>
  );
}
