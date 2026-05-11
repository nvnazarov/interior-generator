import { type Furniture, type Wall } from "../../api/entities";
import * as THREE from "three";
import { CM, M, snapToGridVector3 } from "../lib";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import {
  furniturePreviewUpdated,
  hideFurniturePreview,
  hideHint,
  selectFurnitureDrag,
  showFurniturePreview,
  showHint,
} from "../slice";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLazyGetFurnitureByIdQuery } from "../../api/slice";
import type { ThreeEvent } from "@react-three/fiber";

export function WallMesh({ wall }: { wall: Wall }) {
  const dispatch = useAppDispatch();
  const furnitureDrag = useAppSelector(selectFurnitureDrag);
  const [furniture, setFurniture] = useState<Furniture | null>(null);
  const [getFurnitureById] = useLazyGetFurnitureByIdQuery();

  const start = new THREE.Vector3(wall.x1, 0, wall.y1);
  const end = new THREE.Vector3(wall.x2, 0, wall.y2);
  const length = start.distanceTo(end) + 20 * CM;
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start).normalize();
  const angle = Math.atan2(direction.z, direction.x);

  const l = +(start.distanceTo(end) / M).toFixed(2);

  useEffect(() => {
    if (furnitureDrag) {
      getFurnitureById(furnitureDrag.furnitureId)
        .unwrap()
        .then((f) => setFurniture(f));
    }
  }, [furnitureDrag]);

  const handlePointerMove = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      e.stopPropagation();
      dispatch(
        showHint({
          title: "Несущая стена",
          length: l,
          x: e.clientX,
          y: e.clientY,
        }),
      );
      if (furnitureDrag && furniture) {
        const normal = e.normal?.clone();
        if (!normal) {
          return;
        }
        normal.applyQuaternion(e.object.quaternion).normalize();
        const yaw = Math.atan2(normal.x, normal.z);
        normal.multiplyScalar(furniture.depth / 2);
        let point = e.point.add(normal);
        switch (furniture.mount) {
          case "floor": {
            point.y = furniture.height / 2;
            break;
          }
          case "ceiling": {
            point.y = 3 * M - furniture.height / 2;
            break;
          }
          case "wall": {
            break;
          }
        }
        point = snapToGridVector3(point, CM);
        dispatch(
          furniturePreviewUpdated({
            x: point.x,
            y: point.y,
            z: point.z,
            yaw: yaw,
          }),
        );
      }
    },
    [furnitureDrag, furniture, l],
  );

  const handlePointerOut = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      dispatch(hideHint());
      if (furnitureDrag) {
        e.stopPropagation();
        dispatch(hideFurniturePreview());
      }
    },
    [furnitureDrag],
  );

  const handlePointerEnter = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      if (furnitureDrag && furniture) {
        e.stopPropagation();
        const point = snapToGridVector3(e.point, CM);
        dispatch(
          showFurniturePreview({
            furnitureId: furnitureDrag.furnitureId,
            x: point.x,
            y: point.y,
            z: point.z,
            yaw: 0,
          }),
        );
      }
    },
    [furnitureDrag, furniture],
  );

  const mesh = useMemo(
    () => (
      <mesh
        position={[center.x, (3 * M) / 2, center.z]}
        rotation={[0, -angle, 0]}
        onPointerEnter={handlePointerEnter}
        onPointerMove={handlePointerMove}
        onPointerOut={handlePointerOut}
      >
        <boxGeometry args={[length, 3 * M, 20 * CM]} />
        <meshStandardMaterial color="white" />
      </mesh>
    ),
    [handlePointerEnter, handlePointerMove, handlePointerOut],
  );

  return mesh;
}
