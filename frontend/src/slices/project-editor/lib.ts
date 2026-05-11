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
