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
import { selectPlanEditorTool, selectPlanEditorView } from "./slice";
import { M } from "./lib";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import { PlanMesh } from "./PlanMesh";
import { AreaTool } from "./AreaTool";

const { ACTION } = CameraControlsImpl;

export function Scene() {
  const menu = useContextMenu();
  const view = useAppSelector(selectPlanEditorView);
  const tool = useAppSelector(selectPlanEditorTool);
  const toolIsHand = tool === "hand";
  const toolIsFurinture = tool === "furniture";
  const toolIsArea = tool === "area";

  return (
    <Canvas
      onPointerDown={() => menu.hide()}
      gl={{ logarithmicDepthBuffer: true }}
    >
      <ambientLight intensity={0.15} />
      <directionalLight position={[5, 5, 3]} intensity={1} />
      <directionalLight position={[-3, 2, 4]} intensity={0.4} color="#ffaa88" />
      <directionalLight position={[0, 3, -5]} intensity={0.6} color="#88aaff" />
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
            far={100 * M}
            zoom={1}
            near={0.1}
            makeDefault
          />
          <CameraControls
            mouseButtons={{
              left: toolIsFurinture ? ACTION.NONE : ACTION.ROTATE,
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
      <PlanMesh />
      {toolIsArea && <AreaTool />}
      {/* <ProjectMesh />
      {toolIsWall && <WallTool />}
      {toolIsWetArea && <WetAreaTool />} */}
    </Canvas>
  );
}
