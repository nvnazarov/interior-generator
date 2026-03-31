import { Vector3 } from "three";

export const CM = 1;
export const M = 100;

export function snapToGrid([x, z]: [x: number, z: number], cellSize: number): [number, number] {
  const h = cellSize / 2;
  return [Math.floor((x + h) / cellSize) * cellSize, Math.floor((z + h) / cellSize) * cellSize];
}

export function snapToGridVector3(v: Vector3, size: number): Vector3 {
  return new Vector3().add(v).addScalar(size / 2).divideScalar(size).floor().multiplyScalar(size);
}