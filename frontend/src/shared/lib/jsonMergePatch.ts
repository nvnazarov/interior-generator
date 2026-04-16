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

export function computeJsonMergePatch<T>(source: T, target: T): any {
  if (source === target) {
    return {};
  }
  if (target === null) {
    return null;
  }
  if (source === null) {
    return target;
  }
  const sourceIsObject = source !== null && typeof source === "object" && !Array.isArray(source);
  const targetIsObject = target !== null && typeof target === "object" && !Array.isArray(target)
  if (!sourceIsObject || !targetIsObject) {
    return target;
  }
  const result: any = {};
  const allKeys = new Set([...Object.keys(source), ...Object.keys(target)]);
  for (const key of allKeys) {
    const sourceValue = (source as any)[key];
    const targetValue = (target as any)[key];
    if (sourceValue === targetValue) {
      continue;
    }
    if (!(key in source)) {
      if (targetValue !== undefined) {
        result[key] = targetValue;
      }
      continue;
    }
    if (!(key in target)) {
      result[key] = null;
      continue;
    }
    const nestedPatch = computeJsonMergePatch(sourceValue, targetValue);
    if (nestedPatch !== undefined) {
      result[key] = nestedPatch;
    }
  }
  return Object.keys(result).length > 0 ? result : {};
}