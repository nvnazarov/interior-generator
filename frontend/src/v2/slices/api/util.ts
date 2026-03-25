export function mapById<T, U>(
  obj: Record<string, T>,
  f: (v: T) => U,
): Record<string, U> {
  const result: Record<string, U> = {};
  for (const [k, v] of Object.entries(obj)) {
    result[k] = f(v);
  }
  return result;
}
