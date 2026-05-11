import type { WetArea } from "../../api/entities";
import * as THREE from "three";
import { useCallback, useMemo, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { useContextMenu } from "../../../shared/hooks/contextMenu";
import { projectChanged } from "../slice";
import { useAppDispatch } from "../../storeTypes";
import { useTranslation } from "react-i18next";

export function WetAreaMesh({ area }: { area: WetArea & { id: string } }) {
  const dispatch = useAppDispatch();
  const menu = useContextMenu();
  const [hovered, setHovered] = useState(false);
  const { t } = useTranslation();

  const shape = useMemo(() => {
    const points = area.points;
    const shape = new THREE.Shape();
    shape.moveTo(points[0]!.x, points[0]!.y);
    for (let i = 1; i < points.length; i++) {
      shape.lineTo(points[i]!.x, points[i]!.y);
    }
    shape.closePath();
    return shape;
  }, [area.points]);

  const handleContextMenu = useCallback(
    (e: ThreeEvent<MouseEvent>) => {
      e.stopPropagation();
      menu.show({
        title: "Wet Area",
        x: e.clientX,
        y: e.clientY,
        items: [
          {
            name: t("ProjectEditor.WetAreaMesh.DeleteOption.Title", "Delete"),
            onClick: () => {
              dispatch(
                projectChanged({
                  patch: {
                    content: {
                      wetAreas: {
                        [area.id]: null,
                      },
                    },
                  },
                  inversePatch: {
                    content: {
                      wetAreas: {
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
    },
    [area],
  );

  const handlePointerEnter = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(true);
    e.stopPropagation();
  }, []);

  const handlePointerOut = useCallback((e: ThreeEvent<PointerEvent>) => {
    setHovered(false);
    e.stopPropagation();
  }, []);

  return (
    <mesh
      rotation={[Math.PI / 2, 0, 0]}
      onContextMenu={handleContextMenu}
      onPointerEnter={handlePointerEnter}
      onPointerOut={handlePointerOut}
    >
      <shapeGeometry args={[shape]} />
      <meshStandardMaterial
        color={hovered ? "hotpink" : "lightblue"}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}
