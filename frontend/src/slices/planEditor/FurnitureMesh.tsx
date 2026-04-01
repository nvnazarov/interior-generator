import { useCallback, useState } from "react";
import type { FurnitureInPlan } from "../api/entities";
import { useGetFurnitureByIdQuery } from "../api/slice";
import { CM } from "./lib";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import type { ThreeEvent } from "@react-three/fiber";
import { useAppDispatch } from "../storeTypes";
import { planChanged } from "./slice";

export function FurnitureMesh({ furniture }: { furniture: FurnitureInPlan }) {
  const dispatch = useAppDispatch();
  const { data, isSuccess } = useGetFurnitureByIdQuery(furniture.furnitureId);
  const menu = useContextMenu();
  const [hovered, setHovered] = useState(false);

  const handleContextMenu = useCallback(
    (e: ThreeEvent<MouseEvent>) => {
      if (isSuccess) {
        e.stopPropagation();
        menu.show({
          title: data.name,
          x: e.clientX,
          y: e.clientY,
          items: [
            {
              name: "Delete",
              onClick: () => {
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
              },
            },
          ],
        });
      } else {
        menu.show({
          title: "Loading furniture",
          x: e.clientX,
          y: e.clientY,
          items: [],
        });
      }
    },
    [isSuccess],
  );

  const handlePointerEnter = useCallback((e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHovered(true);
  }, []);

  const handlePointerLeave = useCallback((e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHovered(false);
  }, []);

  return isSuccess ? (
    <mesh
      position={[furniture.x, furniture.y, furniture.z]}
      rotation={[0, furniture.yaw, 0]}
      onContextMenu={handleContextMenu}
      onPointerEnter={handlePointerEnter}
      onPointerLeave={handlePointerLeave}
    >
      <boxGeometry args={[data.width, data.height, data.depth]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "green"} />
    </mesh>
  ) : (
    <mesh
      position={[furniture.x, furniture.y, furniture.z]}
      rotation={[0, furniture.yaw, 0]}
      onContextMenu={handleContextMenu}
    >
      <boxGeometry args={[CM, CM, CM]} />
      <meshStandardMaterial color="black" />
    </mesh>
  );
}
