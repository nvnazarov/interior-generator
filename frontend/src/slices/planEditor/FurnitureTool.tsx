import { useThree } from "@react-three/fiber";
import { useAppSelector } from "../storeTypes";
import { CM, M, snapToGrid } from "./lib";
import { selectFurnitureDrag } from "./slice";
import { useCallback } from "react";
import * as THREE from "three";

export function FurnitureTool() {
  const { camera, raycaster } = useThree();
  const furnitureDrag = useAppSelector(selectFurnitureDrag);

  const getMousePosition = useCallback(
    (e: React.MouseEvent): [number, number] | null => {
      const mouse = new THREE.Vector2(
        (e.clientX / window.innerWidth) * 2 - 1,
        -(e.clientY / window.innerHeight) * 2 + 1,
      );
      raycaster.setFromCamera(mouse, camera);
      const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
      const target = new THREE.Vector3();
      if (raycaster.ray.intersectPlane(plane, target)) {
        return snapToGrid([target.x, target.z], 1 * CM);
      }
      return null;
    },
    [camera, raycaster],
  );

  return <></>;
}
