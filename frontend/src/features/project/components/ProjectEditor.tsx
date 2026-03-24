import * as THREE from "three";
import React, { useMemo, useState } from "react";
import "./ProjectEditor.scss";
import { Canvas, useThree, type ThreeEvent } from "@react-three/fiber";
import { type Wall, type Window } from "../project";
import { v4 as uuidv4 } from "uuid";
import {
  recordProjectChange,
  selectProjectEditor,
  selectProjectEditorProject,
} from "../slice";
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import {
  CameraControls,
  OrbitControls,
  OrthographicCamera,
  CameraControlsImpl,
} from "@react-three/drei";

const { ACTION } = CameraControlsImpl;
const WALL_HEIGHT = 300;
const WALL_DEPTH = 20;
const WINDOW_DEPTH = 24;

export interface Props {
  id: string;
}

export function WindowObject({ id }: { id: string }) {
  const project = useAppSelector(selectProjectEditorProject);
  const [hovered, hover] = useState(false);
  if (!project) {
    return <></>;
  }
  const window = project.content.windows[id];
  if (!window) {
    return <></>;
  }
  const wall = project.content.walls[window.wallId];
  if (!wall) {
    return <></>;
  }

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

  function handlePointerOver(e: ThreeEvent<PointerEvent>) {
    e.stopPropagation();
    hover(true);
  }

  function handlePointerOut(_: ThreeEvent<PointerEvent>) {
    hover(false);
  }

  return (
    <mesh
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
      position={[center.x, window.y + window.h / 2, center.z]}
      rotation={[0, -angle, 0]}
    >
      <boxGeometry args={[length, window.h, WINDOW_DEPTH]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "blue"} />
    </mesh>
  );
}

export function WallObject({ wall }: { wall: Wall }) {
  const dispatch = useAppDispatch();
  const editor = useAppSelector(selectProjectEditor);
  const [hovered, hover] = useState(false);
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null);
  const [endPoint, setEndPoint] = useState<[number, number] | null>(null);

  const start = new THREE.Vector3(wall.x1, 0, wall.y1);
  const end = new THREE.Vector3(wall.x2, 0, wall.y2);
  const length = start.distanceTo(end);
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

  function getWallLocalPoint(worldPoint: THREE.Vector3): [number, number] {
    const localPoint = worldPoint
      .clone()
      .applyMatrix4(worldToWallMatrix.clone().invert());
    return [Math.floor(localPoint.x), Math.floor(localPoint.y)];
  }

  function handlePointerOver(e: ThreeEvent<PointerEvent>) {
    if (editor.activeTool !== "wall") {
      e.stopPropagation();
      hover(true);
    }
  }

  function handlePointerOut(_: ThreeEvent<PointerEvent>) {
    hover(false);
  }

  function handlePointerDown(e: ThreeEvent<PointerEvent>) {
    if (editor.activeTool === "window" || editor.activeTool === "door") {
      setStartPoint(getWallLocalPoint(e.point));
      setEndPoint(null);
    }
  }

  function handlePointerMove(e: ThreeEvent<PointerEvent>) {
    if (editor.activeTool === "window" || editor.activeTool === "door") {
      setEndPoint(getWallLocalPoint(e.point));
    }
  }

  function handlePointerUp(_: ThreeEvent<PointerEvent>) {
    if (!startPoint || !endPoint) return;
    const x1 = Math.min(startPoint[0], endPoint[0]);
    const x2 = Math.max(startPoint[0], endPoint[0]);
    const y1 = Math.min(startPoint[1], endPoint[1]);
    const y2 = Math.max(startPoint[1], endPoint[1]);
    if (editor.activeTool === "window" && editor.viewMode === "3d") {
      const newWindow: Window = {
        id: uuidv4(),
        wallId: wall.id,
        x: x1,
        y: y1,
        w: x2 - x1,
        h: y2 - y1,
      };
      dispatch(
        recordProjectChange({
          patch: {
            content: {
              windows: {
                [newWindow.id]: newWindow,
              },
            },
          },
          inversePatch: {
            content: {
              windows: {
                [newWindow.id]: null,
              },
            },
          },
        }),
      );
    }
  }

  function handlePointerLeave(_: ThreeEvent<PointerEvent>) {
    if (startPoint) {
      setStartPoint(null);
      setEndPoint(null);
    }
  }

  const showPreview =
    startPoint &&
    endPoint &&
    (editor.activeTool === "window" || editor.activeTool === "door");

  return (
    <mesh
      position={[center.x, WALL_HEIGHT / 2, center.z]}
      rotation={[0, -angle, 0]}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerLeave}
    >
      <boxGeometry args={[length, WALL_HEIGHT, WALL_DEPTH]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "white"} />
    </mesh>
  );
}

export function Walls() {
  const dispatch = useAppDispatch();
  const editor = useAppSelector(selectProjectEditor);
  const project = useAppSelector(selectProjectEditorProject);
  const isMode2D = editor.viewMode === "2d";
  const isWallTool = editor.activeTool === "wall";

  if (!project) {
    throw new Error("BUG");
  }

  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null);
  const [previewEndPoint, setPreviewEndPoint] = useState<
    [number, number] | null
  >(null);

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
      return [Math.floor(target.x), Math.floor(target.z)];
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
          id: uuidv4(),
          x1: startPoint[0],
          y1: startPoint[1],
          x2: endPoint[0],
          y2: endPoint[1],
        };
        dispatch(
          recordProjectChange({
            patch: { content: { walls: { [newWall.id]: newWall } } },
            inversePatch: { content: { walls: { [newWall.id]: null } } },
          }),
        );
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
      {Object.entries(project.content.walls).map(([key, wall]) => (
        <WallObject key={key} wall={wall} />
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

export function Windows() {
  const project = useAppSelector(selectProjectEditorProject);
  if (!project) {
    return <></>;
  }
  return (
    <>
      {Object.keys(project.content.windows).map((key) => (
        <WindowObject key={key} id={key} />
      ))}
    </>
  );
}

export function ProjectEditor() {
  const editor = useAppSelector(selectProjectEditor);
  const isMode2D = editor.viewMode === "2d";
  const isHandTool = editor.activeTool === "hand";
  const isWindowOrDoorTool =
    editor.activeTool === "window" || editor.activeTool === "door";

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
        <OrbitControls
          maxPolarAngle={0}
          mouseButtons={{
            LEFT: isHandTool ? THREE.MOUSE.PAN : undefined,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: isHandTool ? THREE.MOUSE.ROTATE : THREE.MOUSE.PAN,
          }}
          makeDefault
        />
      ) : (
        <CameraControls
          mouseButtons={{
            left: isWindowOrDoorTool ? ACTION.NONE : ACTION.ROTATE,
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
      <Windows />
    </Canvas>
  );
}
