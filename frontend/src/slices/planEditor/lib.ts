import { Color, Vector3 } from "three";
import type { FunctionalArea } from "../api/entities";

export const { BLUE, RED, YELLOW, GREEN, GREY } = {
  BLUE: new Color().setRGB(0.5, 0.5, 1),
  RED: new Color().setRGB(1, 0.5, 0.5),
  YELLOW: new Color().setRGB(1, 1, 0.5),
  GREEN: new Color().setRGB(0.5, 1, 0.5),
  GREY: new Color().setRGB(0.8, 0.8, 0.8),
};

export const CM = 1;
export const M = 100;

export function snapToGrid(
  [x, z]: [x: number, z: number],
  cellSize: number,
): [number, number] {
  const h = cellSize / 2;
  return [
    Math.floor((x + h) / cellSize) * cellSize,
    Math.floor((z + h) / cellSize) * cellSize,
  ];
}

export function snapToGridVector3(v: Vector3, size: number): Vector3 {
  return new Vector3()
    .add(v)
    .addScalar(size / 2)
    .divideScalar(size)
    .floor()
    .multiplyScalar(size);
}

export function areaColorByType(type: FunctionalArea["type"]): Color {
  switch (type) {
    case "kitchen":
      return RED;
    case "bathroom":
      return BLUE;
    case "bedroom":
      return GREEN;
    case "hallway":
      return GREY;
    case "livingroom":
      return YELLOW;
    default:
      return GREY;
  }
}
