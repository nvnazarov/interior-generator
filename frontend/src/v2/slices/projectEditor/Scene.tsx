import {
  CameraControls,
  CameraControlsImpl,
  Grid,
  OrbitControls,
  OrthographicCamera,
  PerspectiveCamera,
} from "@react-three/drei";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { useAppSelector } from "../storeTypes";
import { selectProjectEditorTool, selectProjectEditorView } from "./slice";
import { M } from "./lib";
import { ProjectMesh } from "./ProjectMesh";
import { WallTool } from "./WallTool";
import { WetAreaTool } from "./WetAreaTool";

const { ACTION } = CameraControlsImpl;

export function Scene() {
  const view = useAppSelector(selectProjectEditorView);
  const tool = useAppSelector(selectProjectEditorTool);
  const toolIsHand = tool === "hand";
  const toolIsWall = tool === "wall";
  const toolIsWetArea = tool === "wet_area";
  const toolIsDoorOrWindow = ["window", "door"].includes(tool);

  return (
    <Canvas>
      <ambientLight intensity={1} />
      <directionalLight position={[5, 5, 5]} />
      {view === "2D" ? (
        <>
          <OrthographicCamera
            position={[0, 4 * M, 0]}
            rotation={[-Math.PI / 2, 0, 0]}
            far={100 * M}
            zoom={0.5}
            near={0.01}
            makeDefault
          />
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
        </>
      ) : (
        <>
          <PerspectiveCamera
            position={[0, 20 * M, 0]}
            rotation={[-Math.PI / 2, 0, 0]}
            far={10000 * M}
            zoom={1}
            near={0.01}
            makeDefault
          />
          <CameraControls
            mouseButtons={{
              left: toolIsDoorOrWindow ? ACTION.NONE : ACTION.ROTATE,
              middle: ACTION.ROTATE,
              wheel: ACTION.DOLLY,
              right: ACTION.TRUCK,
            }}
            makeDefault
          />
        </>
      )}
      <Grid
        cellColor="lightgrey"
        sectionColor="lightgrey"
        cellSize={1 * M}
        sectionSize={1 * M}
        fadeDistance={100 * M}
        fadeStrength={0}
        side={THREE.DoubleSide}
        infiniteGrid
      />
      <ProjectMesh />
      {toolIsWall && <WallTool />}
      {toolIsWetArea && <WetAreaTool />}
    </Canvas>
  );
}
