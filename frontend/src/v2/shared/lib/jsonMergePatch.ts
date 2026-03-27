export function applyJsonMergePatch<T>(target: T, patch: any): T {
  if (patch === null || typeof patch !== "object" || Array.isArray(patch)) {
    return patch as T;
  }
  const result: any =
    target !== null && typeof target === "object" && !Array.isArray(target)
      ? { ...target }
      : {};
  for (const key of Object.keys(patch)) {
    const patchValue = patch[key];
    if (patchValue === null) {
      delete result[key];
    } else if (typeof patchValue === "object" && !Array.isArray(patchValue)) {
      const currentValue = result[key];
      result[key] = applyJsonMergePatch(currentValue, patchValue);
    } else {
      result[key] = patchValue;
    }
  }
  return result as T;
}

export function combineJsonMergePatches(a: any, b: any): any {
  const result = { ...a };
  for (const bKey of Object.keys(b)) {
    const v = b[bKey];
    if (v === null) {
      result[bKey] = null;
    } else if (
      typeof v === "object" &&
      !Array.isArray(v) &&
      typeof result[bKey] === "object" &&
      !Array.isArray(result[bKey]) &&
      result[bKey] !== null
    ) {
      result[bKey] = combineJsonMergePatches(result[bKey], v);
    } else {
      result[bKey] = v;
    }
  }
  return result;
}

export function combineManyJsonMergePatches(patches: any[]): any {
  if (patches.length === 0) return {};
  if (patches.length === 1) return patches[0]!;
  let result: any = {};
  for (const patch of patches) {
    result = combineJsonMergePatches(result, patch);
  }
  return result;
}
