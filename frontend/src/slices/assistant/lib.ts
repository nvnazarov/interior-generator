const SECOND_MS = 1000;
const MINUTE_MS = 60 * SECOND_MS;
const HOUR_MS = 60 * MINUTE_MS;

export function human(ms: number): string {
  const parts = [] as string[];
  if (ms >= HOUR_MS) {
    parts.push(Math.round(ms / HOUR_MS) + "h");
    ms %= HOUR_MS;
  }
  if (ms >= MINUTE_MS) {
    parts.push(Math.round(ms / MINUTE_MS) + "m");
    ms %= MINUTE_MS;
  }
  if (ms >= SECOND_MS) {
    parts.push(Math.round(ms / SECOND_MS) + "s");
    ms %= SECOND_MS;
  }
  if (parts.length === 0) {
    parts.push(ms + "ms");
  }
  return parts.slice(0, 2).reduce((prev, v) => {
    if (v.startsWith("0")) {
      return prev;
    }
    return prev + v;
  });
}
