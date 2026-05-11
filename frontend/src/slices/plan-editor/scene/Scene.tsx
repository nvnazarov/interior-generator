import {
  CameraControls,
  CameraControlsImpl,
  GizmoHelper,
  GizmoViewport,
  Grid,
  OrbitControls,
  OrthographicCamera,
  PerspectiveCamera,
} from "@react-three/drei";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import {
  finishedDraggingFurniture,
  planChanged,
  selectFurnitureDrag,
  selectPlanEditor,
  selectPlanEditorTool,
  selectPlanEditorView,
} from "../slice";
import { M } from "../lib";
import { useContextMenu } from "../../../shared/hooks/contextMenu";
import { PlanMesh } from "./PlanMesh";
import { AreaTool } from "./AreaTool";
import { FurniturePreview } from "./FurniturePreview";
import { useEffect } from "react";
import type { FurnitureInPlan } from "../../api/entities";
import { v4 as uuidv4 } from "uuid";
import { FurnitureTool } from "./FurnitureTool";

const { ACTION } = CameraControlsImpl;

function DragHelper() {
  const dispatch = useAppDispatch();
  const furnitureDrag = useAppSelector(selectFurnitureDrag);
  const preview = useAppSelector(
    (state) => selectPlanEditor(state).furniturePreview,
  );

  useEffect(() => {
    if (furnitureDrag) {
      function handleMouseUp() {
        if (!preview) {
          return;
        }
        const furniture: FurnitureInPlan = {
          id: uuidv4(),
          furnitureId: preview.furnitureId,
          x: preview.x,
          y: preview.y,
          z: preview.z,
          yaw: preview.yaw,
        };
        dispatch(
          planChanged({
            patch: {
              content: {
                furniture: {
                  [furniture.id]: furniture,
                },
              },
            },
            inversePatch: {
              content: {
                furniture: {
                  [furniture.id]: null,
                },
              },
            },
          }),
        );
        dispatch(finishedDraggingFurniture());
      }

      window.addEventListener("mouseup", handleMouseUp);
      return () => {
        window.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [furnitureDrag, preview]);

  return <></>;
}

export function Scene() {
  const menu = useContextMenu();
  const view = useAppSelector(selectPlanEditorView);
  const tool = useAppSelector(selectPlanEditorTool);
  const furnitureDrag = useAppSelector(selectFurnitureDrag);
  const toolIsHand = tool === "hand";
  const toolIsFurinture = tool === "furniture" || furnitureDrag;
  const toolIsArea = tool === "area" && !furnitureDrag;

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
      <FurniturePreview />
      <DragHelper />
      {view === "3D" && (
        <GizmoHelper alignment="bottom-right" margin={[80, 80]}>
          <GizmoViewport
            axisColors={["red", "green", "blue"]}
            labelColor="black"
          />
        </GizmoHelper>
      )}
      {toolIsArea && <AreaTool />}
      {toolIsFurinture && <FurnitureTool />}
    </Canvas>
  );
}
