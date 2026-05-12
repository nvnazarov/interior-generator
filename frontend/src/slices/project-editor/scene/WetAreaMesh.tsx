import type { WetArea } from "../../api/entities";
import * as THREE from "three";
import { useCallback, useMemo, useState } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import { projectChanged } from "../slice";
import { useAppDispatch } from "../../storeTypes";
import { ContextMenuOption, MeshMenu } from "../../../shared/components";
import { computePolygonArea } from "../lib";

export function WetAreaMesh({ area }: { area: WetArea & { id: string } }) {
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
  }, [area]);

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
          Wet area
          <br />
          <br /> <b>Area:</b> {areaSqm} sq m
        </>
      }
      menu={
        <>
          <ContextMenuOption text="Delete wet area" onClick={handleDelete} />
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
          color={hovered ? "hotpink" : "lightblue"}
          side={THREE.DoubleSide}
        />
      </mesh>
    </MeshMenu>
  );
}
