export function human(ms: number): string {
  if (ms < 1000) {
    return ms + "ms";
  }
  return Math.round(ms / 1000) + "s";
}
