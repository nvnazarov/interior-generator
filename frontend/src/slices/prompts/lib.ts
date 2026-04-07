export function human(ms: number): string {
  if (ms < 1000) {
    return ms + "ms"
  }
  return Math.floor(ms / 1000) + "s";
}