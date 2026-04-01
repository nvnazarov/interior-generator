import { type ThreeEvent } from "@react-three/fiber";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { CM, M, snapToGridVector3 } from "./lib";
import { furniturePreviewUpdated, selectFurnitureDrag } from "./slice";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { Furniture } from "../api/entities";
import { useLazyGetFurnitureByIdQuery } from "../api/slice";

export function FurnitureTool() {
  const dispatch = useAppDispatch();
  const [furniture, setFurniture] = useState<Furniture | null>(null);
  const furnitureDrag = useAppSelector(selectFurnitureDrag);
  const [getFurnitureById] = useLazyGetFurnitureByIdQuery();

  useEffect(() => {
    if (furnitureDrag) {
      getFurnitureById(furnitureDrag.furnitureId)
        .unwrap()
        .then((f) => setFurniture(f));
    }
  }, [furnitureDrag]);

  const handlePointerMove = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      if (furnitureDrag && furniture) {
        e.stopPropagation();
        let point = e.point;
        // switch (furniture.mount) {
        //   case "floor": {
        //     point.y = furniture.height / 2;
        //     break;
        //   }
        //   case "ceiling": {
        //     point.y = 3 * M - furniture.height / 2;
        //     break;
        //   }
        //   case "wall": {
        //     return;
        //   }
        // }
        point = snapToGridVector3(point, CM);
        dispatch(
          furniturePreviewUpdated({
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

  const mesh = useMemo(() => {
    return (
      <mesh
        position={[0, 0, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerMove={handlePointerMove}
      >
        <planeGeometry args={[1000 * M, 1000 * M]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
    );
  }, [furnitureDrag, furniture]);

  return mesh;
}
