import { useEffect, useRef, useState } from "react";
import { useThree } from "@react-three/fiber";
import { v4 as uuidv4 } from "uuid";

import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { M } from "../lib";
import {
  finishedDraggingFurniture,
  planChanged,
  planUndoablyChanged,
  selectFurnitureDrag,
} from "../slice";
import { useLazyGetFurnitureByIdQuery } from "../../api/slice";
import type { Furniture } from "../../api/entities";
import { Object3D, Raycaster, Vector2 } from "three";
import { WALL_HEIGHT } from "../../project-editor/lib";

type Position = {
  x: number;
  y: number;
  z: number;
  yaw: number;
};

function FurniturePreview({
  furniture,
  position,
}: {
  furniture: Furniture;
  position: Position;
}) {
  return (
    <mesh
      position={[position.x, position.y, position.z]}
      rotation={[0, position.yaw, 0]}
      userData={{ preview: true }}
    >
      <boxGeometry
        args={[furniture.width, furniture.height, furniture.depth]}
      />
      <meshStandardMaterial color="green" />
    </mesh>
  );
}

export function FurnitureTool() {
  const dispatch = useAppDispatch();
  const furnitureDrag = useAppSelector(selectFurnitureDrag);
  const [position, setPosition] = useState<Position>({
    x: 0,
    y: 0,
    z: 0,
    yaw: 0,
  });
  const { camera, gl, scene } = useThree();
  const raycaster = useRef(new Raycaster());
  const [getFurnitureById, { data: furniture }] =
    useLazyGetFurnitureByIdQuery();
  const objects = useRef<Object3D[]>([]);

  useEffect(() => {
    if (furnitureDrag) {
      getFurnitureById(furnitureDrag.furnitureId);
    }
  }, [furnitureDrag]);

  useEffect(() => {
    if (furnitureDrag?.furnitureInPlan) {
      setPosition(furnitureDrag.furnitureInPlan);
      dispatch(
        planUndoablyChanged({
          content: {
            furniture: {
              [furnitureDrag.furnitureInPlan.id]: null,
            },
          },
        }),
      );
    }
  }, [furnitureDrag]);

  useEffect(() => {
    scene.traverse((object) => {
      if (object.visible && !object.userData.preview) {
        objects.current.push(object);
      }
    });
  }, [furnitureDrag]);

  useEffect(() => {
    if (!furnitureDrag || !furniture) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = gl.domElement.getBoundingClientRect();
      const mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      const mouse = new Vector2(mouseX, mouseY);

      raycaster.current.setFromCamera(mouse, camera);
      const intersections = raycaster.current.intersectObjects(
        objects.current,
        false,
      );
      if (intersections.length > 0) {
        const hit = intersections[0]!;
        const normal = hit.face?.normal.clone();
        if (!normal) {
          setPosition({
            x: hit.point.x,
            y: hit.point.y,
            z: hit.point.z,
            yaw: 0,
          });
          return;
        } else {
          normal.applyQuaternion(hit.object.quaternion);
          normal.normalize();
          switch (furniture.mount) {
            case "wall": {
              if (normal.y !== 0) break;
              const center = hit.point.add(
                normal.multiplyScalar(furniture.depth / 2),
              );
              setPosition({
                x: center.x,
                y: center.y,
                z: center.z,
                yaw: Math.atan2(normal.x, normal.z),
              });
              return;
            }
            case "ceiling": {
              if (normal.y !== 0) {
                const center = hit.point;
                setPosition({
                  x: center.x,
                  y: WALL_HEIGHT - furniture.height / 2,
                  z: center.z,
                  yaw: Math.atan2(normal.x, normal.z),
                });
                return;
              } else {
                const center = hit.point.add(
                  normal.multiplyScalar(furniture.depth / 2),
                );
                setPosition({
                  x: center.x,
                  y: WALL_HEIGHT - furniture.height / 2,
                  z: center.z,
                  yaw: Math.atan2(normal.x, normal.z),
                });
                return;
              }
            }
            case "floor": {
              if (normal.y !== 0) {
                const center = hit.point;
                setPosition({
                  x: center.x,
                  y: furniture.height / 2,
                  z: center.z,
                  yaw: Math.atan2(normal.x, normal.z),
                });
                return;
              } else {
                const center = hit.point.add(
                  normal.multiplyScalar(furniture.depth / 2),
                );
                setPosition({
                  x: center.x,
                  y: furniture.height / 2,
                  z: center.z,
                  yaw: Math.atan2(normal.x, normal.z),
                });
                return;
              }
            }
            case "surface": {
              if (normal.y > 0.8) {
                const center = hit.point;
                setPosition({
                  x: center.x,
                  y: center.y + furniture.height / 2,
                  z: center.z,
                  yaw: 0,
                });
                return;
              } else {
                const center = hit.point.add(
                  normal.multiplyScalar(furniture.depth / 2),
                );
                setPosition({
                  x: center.x,
                  y: furniture.height / 2,
                  z: center.z,
                  yaw: Math.atan2(normal.x, normal.z),
                });
                return;
              }
            }
          }
        }
      }
      setPosition({ x: 0, y: furniture.height / 2, z: 0, yaw: 0 });
    };

    const handleClick = () => {
      const id = furnitureDrag.furnitureInPlan?.id || uuidv4();
      dispatch(
        planChanged({
          patch: {
            content: {
              furniture: {
                [id]: {
                  furnitureId: furniture.id,
                  x: Math.floor(position.x),
                  y: Math.floor(position.y),
                  z: Math.floor(position.z),
                  yaw: position.yaw,
                },
              },
            },
          },
          inversePatch: {
            content: {
              furniture: {
                [id]: furnitureDrag.furnitureInPlan
                  ? (() => {
                      const { id, ...rest } = furnitureDrag.furnitureInPlan;
                      return rest;
                    })()
                  : null,
              },
            },
          },
        }),
      );
      dispatch(finishedDraggingFurniture());
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("click", handleClick);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("click", handleClick);
    };
  }, [furnitureDrag, furniture, camera, gl, scene, position]);

  return (
    <>
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[1000 * M, 1000 * M]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      {furniture && furnitureDrag && (
        <FurniturePreview furniture={furniture} position={position} />
      )}
    </>
  );
}
