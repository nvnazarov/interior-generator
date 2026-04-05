import type { FunctionalArea } from "../api/entities";
import * as THREE from "three";
import { useCallback, useMemo, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { useContextMenu } from "../../shared/hooks/contextMenu";
import { hideHint, planChanged, showHint } from "./slice";
import { useAppDispatch } from "../storeTypes";
import { useTranslation } from "react-i18next";
import { areaColorByType } from "./lib";

export function AreaMesh({ area }: { area: FunctionalArea }) {
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
        title: area.type,
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
          {
            divider: true,
          },
          ...(
            [
              "kitchen",
              "livingroom",
              "bathroom",
              "bedroom",
              "hallway",
            ] as FunctionalArea["type"][]
          )
            .filter((type) => type !== area.type)
            .map((type) => ({
              name: type,
              onClick: () => {
                dispatch(
                  planChanged({
                    patch: {
                      content: {
                        areas: {
                          [area.id]: {
                            id: area.id,
                            type: type,
                          },
                        },
                      },
                    },
                    inversePatch: {
                      content: {
                        areas: {
                          [area.id]: {
                            id: area.id,
                            type: area.type,
                          },
                        },
                      },
                    },
                  }),
                );
              },
            })),
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
    dispatch(hideHint());
    e.stopPropagation();
  }, []);

  const handlePointerMove = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      e.stopPropagation();
      dispatch(showHint({ title: area.type, x: e.clientX, y: e.clientY }));
    },
    [area],
  );

  return (
    <mesh
      rotation={[Math.PI / 2, 0, 0]}
      onContextMenu={handleContextMenu}
      onPointerEnter={handlePointerEnter}
      onPointerOut={handlePointerOut}
      onPointerMove={handlePointerMove}
    >
      <shapeGeometry args={[shape]} />
      <meshStandardMaterial
        color={hovered ? "hotpink" : areaColorByType(area.type)}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}
