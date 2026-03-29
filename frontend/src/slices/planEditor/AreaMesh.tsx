import { Plane } from "@react-three/drei";
import type { FunctionalArea } from "../api/entities";
import * as THREE from "three";
import { useCallback, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import { planChanged } from "./slice";
import { useAppDispatch } from "../storeTypes";
import { useTranslation } from "react-i18next";

const AREA_MATERIAL = new THREE.MeshStandardMaterial({
  color: "lightblue",
});
const AREA_HOVERED_MATERIAL = new THREE.MeshStandardMaterial({
  color: "hotpink",
});

export function AreaMesh({ area }: { area: FunctionalArea }) {
  const dispatch = useAppDispatch();
  const menu = useContextMenu();
  const [hovered, setHovered] = useState(false);
  const { t } = useTranslation();

  const size = new THREE.Vector3(area.w, 0, area.h);
  const corner = new THREE.Vector3(area.x, 0, area.y);
  const center = new THREE.Vector3().add(size).multiplyScalar(0.5).add(corner);

  const handleContextMenu = useCallback((e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    menu.show({
      title: t("ProjectEditor.WetAreaMesh.Name", "Wet area"),
      x: e.clientX,
      y: e.clientY,
      items: [
        {
          name: t("ProjectEditor.WetAreaMesh.DeleteOption.Title", "Delete"),
          onClick: () => {
            dispatch(
              planChanged({
                patch: {
                  content: {
                    areas: {
                      [area.id]: null,
                    },
                  },
                },
                inversePatch: {
                  content: {
                    areas: {
                      [area.id]: area,
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

  const handlePointerEnter = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(true);
    e.stopPropagation();
  }, []);

  const handlePointerOut = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(false);
    e.stopPropagation();
  }, []);

  return (
    <Plane
      args={[size.x, size.z]}
      position={center}
      rotation={[-Math.PI / 2, 0, 0]}
      material={hovered ? AREA_HOVERED_MATERIAL : AREA_MATERIAL}
      onContextMenu={handleContextMenu}
      onPointerEnter={handlePointerEnter}
      onPointerOut={handlePointerOut}
    />
  );
}
