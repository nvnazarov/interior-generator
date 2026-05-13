import type { FunctionalArea } from "../../api/entities";
import * as THREE from "three";
import { useCallback, useMemo, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { planChanged } from "../slice";
import { useAppDispatch } from "../../storeTypes";
import { areaColorByType, computePolygonArea } from "../lib";
import {
  ContextMenu,
  ContextMenuOption,
  MeshMenu,
} from "../../../shared/components";

export function AreaMesh({ area }: { area: FunctionalArea & { id: string } }) {
  const dispatch = useAppDispatch();
  const [hovered, setHovered] = useState(false);

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

  const handleDelete = useCallback(() => {
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
  }, [area]);

  const handleChangeType = useCallback(
    (type: FunctionalArea["type"]) => {
      dispatch(
        planChanged({
          patch: {
            content: {
              areas: {
                [area.id]: {
                  type: type,
                },
              },
            },
          },
          inversePatch: {
            content: {
              areas: {
                [area.id]: {
                  type: area.type,
                },
              },
            },
          },
        }),
      );
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

  const areaSqm = Math.round(computePolygonArea(area.points));

  return (
    <MeshMenu
      hint={
        <>
          {area.type}
          <br />
          <br /> <b>Area:</b> {areaSqm} sq m
        </>
      }
      menu={
        <>
          <ContextMenuOption text="Delete area" onClick={handleDelete} />
          <ContextMenu
            content={
              <>
                {(
                  [
                    "kitchen",
                    "livingroom",
                    "bedroom",
                    "bathroom",
                    "hallway",
                  ] as FunctionalArea["type"][]
                ).map((type) => (
                  <ContextMenuOption
                    key={type}
                    text={type}
                    onClick={() => handleChangeType(type)}
                  />
                ))}
              </>
            }
            position="right"
          >
            <ContextMenuOption text="Change type" />
          </ContextMenu>
        </>
      }
    >
      <mesh
        rotation={[Math.PI / 2, 0, 0]}
        onPointerEnter={handlePointerEnter}
        onPointerOut={handlePointerOut}
      >
        <shapeGeometry args={[shape]} />
        <meshStandardMaterial
          color={hovered ? "hotpink" : areaColorByType(area.type)}
          side={THREE.DoubleSide}
        />
      </mesh>
    </MeshMenu>
  );
}
