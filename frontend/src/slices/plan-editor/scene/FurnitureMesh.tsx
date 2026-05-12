import { useCallback, useState } from "react";
import type { FurnitureInPlan } from "../../api/entities";
import { useGetFurnitureByIdQuery } from "../../api/slice";
import { CM } from "../lib";
import type { ThreeEvent } from "@react-three/fiber";
import { useAppDispatch } from "../../storeTypes";
import {
  planChanged,
  planUndoablyChanged,
  startedDraggingFurniture,
} from "../slice";

export function FurnitureMesh({
  furniture,
}: {
  furniture: FurnitureInPlan & { id: string };
}) {
  const dispatch = useAppDispatch();
  const { data, isSuccess } = useGetFurnitureByIdQuery(furniture.furnitureId);
  const [hovered, setHovered] = useState(false);

  const handleDelete = useCallback(() => {
    dispatch(
      planChanged({
        patch: {
          content: {
            furniture: {
              [furniture.id]: null,
            },
          },
        },
        inversePatch: {
          content: {
            furniture: {
              [furniture.id]: furniture,
            },
          },
        },
      }),
    );
  }, [furniture]);

  const handlePointerEnter = useCallback((e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHovered(true);
  }, []);

  const handlePointerLeave = useCallback((e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHovered(false);
  }, []);

  const handlePointerDown = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      if (e.button === 0) {
        dispatch(
          planUndoablyChanged({
            content: {
              furniture: {
                [furniture.id]: null,
              },
            },
          }),
        );
        dispatch(
          startedDraggingFurniture({
            furnitureId: furniture.furnitureId,
          }),
        );
      }
    },
    [furniture],
  );

  return isSuccess ? (
    <mesh
      position={[furniture.x, furniture.y, furniture.z]}
      rotation={[0, furniture.yaw, 0]}
      onPointerEnter={handlePointerEnter}
      onPointerLeave={handlePointerLeave}
      onPointerDown={handlePointerDown}
    >
      <boxGeometry args={[data.width, data.height, data.depth]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "green"} />
    </mesh>
  ) : (
    <mesh
      position={[furniture.x, furniture.y, furniture.z]}
      rotation={[0, furniture.yaw, 0]}
    >
      <boxGeometry args={[CM, CM, CM]} />
      <meshStandardMaterial color="black" />
    </mesh>
  );
}
