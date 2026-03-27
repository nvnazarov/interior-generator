import {
  CameraControls,
  CameraControlsImpl,
  Line,
  OrbitControls,
  OrthographicCamera,
} from "@react-three/drei";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { useAppSelector } from "../storeTypes";
import { selectProjectEditorTool, selectProjectEditorView } from "./slice";
import { CM } from "./lib";

const { ACTION } = CameraControlsImpl;

export function Scene() {
  const view = useAppSelector(selectProjectEditorView);
  const tool = useAppSelector(selectProjectEditorTool);
  const toolIsHand = tool === "hand";
  const toolIsDoorOrWindow = tool in ["window", "door"];

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
      {view === "2D" ? (
        <OrbitControls
          maxPolarAngle={0}
          mouseButtons={{
            LEFT: toolIsHand ? THREE.MOUSE.PAN : undefined,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: toolIsHand ? THREE.MOUSE.ROTATE : THREE.MOUSE.PAN,
          }}
          makeDefault
        />
      ) : (
        <CameraControls
          mouseButtons={{
            left: toolIsDoorOrWindow ? ACTION.NONE : ACTION.ROTATE,
            middle: ACTION.ROTATE,
            wheel: ACTION.NONE,
            right: ACTION.TRUCK,
          }}
          makeDefault
        />
      )}
      <Line
        points={[
          [-1000, 0, 0],
          [1000, 0, 0],
        ]}
        color="black"
        lineWidth={1}
      />
      <Line
        points={[
          [0, 0, -1000],
          [0, 0, 1000],
        ]}
        color="black"
        lineWidth={1}
      />
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[1 * CM]} />
        <meshStandardMaterial color="green" />
      </mesh>
    </Canvas>
  );
}
