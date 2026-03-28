import {
  CameraControls,
  CameraControlsImpl,
  Grid,
  OrbitControls,
  OrthographicCamera,
  Sphere,
} from "@react-three/drei";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { useAppSelector } from "../storeTypes";
import { selectProjectEditorTool, selectProjectEditorView } from "./slice";
import { M } from "./lib";
import { ProjectMesh } from "./ProjectMesh";
import { WallTool } from "./WallTool";

const { ACTION } = CameraControlsImpl;

export function Scene() {
  const view = useAppSelector(selectProjectEditorView);
  const tool = useAppSelector(selectProjectEditorTool);
  const toolIsHand = tool === "hand";
  const toolIsWall = tool === "wall";
  const toolIsDoorOrWindow = ["window", "door"].includes(tool);

  return (
    <Canvas>
      <ambientLight intensity={1} />
      <directionalLight position={[5, 5, 5]} />
      <OrthographicCamera
        position={[0, 4 * M, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        far={10 * M}
        zoom={0.5}
        near={0.1}
        makeDefault
      />
      {view === "2D" ? (
        <OrbitControls
          minZoom={0.2}
          maxZoom={5}
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
      <Grid
        cellColor="lightgrey"
        sectionColor="lightgrey"
        cellSize={1 * M}
        sectionSize={1 * M}
        fadeDistance={100 * M}
        fadeStrength={0}
        infiniteGrid
      />
      <ProjectMesh />
      {toolIsWall && <WallTool />}
    </Canvas>
  );
}
