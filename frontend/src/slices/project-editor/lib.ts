export const CM = 1;
export const M = 100;

export const WALL_HEIGHT = 3 * M;
export const WALL_WIDTH = 20 * CM;

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

export function computePolygonArea(points: { x: number; y: number }[]): number {
  let area = 0;
  points.forEach((a, idx) => {
    const b = points[(idx + 1) % points.length]!;
    area += ((a.y + b.y) * (a.x - b.x)) / 2;
  });
  return Math.abs(area) / M / M;
}
