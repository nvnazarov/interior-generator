import { Plane } from "@react-three/drei";
import type { WetArea } from "../api/entities";
import * as THREE from "three";
import { useCallback } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import { projectChanged } from "./slice";
import { useAppDispatch } from "../storeTypes";

const WET_AREA_MATERIAL = new THREE.MeshStandardMaterial({
  color: "lightblue",
});

export function WetAreaMesh({ wetArea }: { wetArea: WetArea }) {
  const dispatch = useAppDispatch();
  const menu = useContextMenu();

  const size = new THREE.Vector3(wetArea.w, 0, wetArea.h);
  const corner = new THREE.Vector3(wetArea.x, 0, wetArea.y);
  const center = new THREE.Vector3().add(size).multiplyScalar(0.5).add(corner);

  const handleContextMenu = useCallback((e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    menu.show({
      title: "Wet area",
      x: e.clientX,
      y: e.clientY,
      items: [
        {
          name: "Delete",
          onClick: () => {
            dispatch(
              projectChanged({
                patch: {
                  content: {
                    wetAreas: {
                      [wetArea.id]: null,
                    },
                  },
                },
                inversePatch: {
                  content: {
                    wetAreas: {
                      [wetArea.id]: wetArea,
                    },
                  },
                },
              }),
            );
          },
        },
      ],
    });
  }, []);

  return (
    <Plane
      args={[size.x, size.z]}
      position={center}
      rotation={[-Math.PI / 2, 0, 0]}
      material={WET_AREA_MATERIAL}
      onContextMenu={handleContextMenu}
    />
  );
}
