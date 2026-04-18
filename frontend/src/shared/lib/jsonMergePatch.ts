export function applyJsonMergePatch(target: any, patch: any): any {
  if (patch === null || typeof patch !== "object" || Array.isArray(patch)) {
    return patch;
  }
  const result: any =
    target !== null && typeof target === "object" && !Array.isArray(target)
      ? { ...target }
      : {};
  for (const key of Object.keys(patch)) {
    const patchValue = patch[key];
    if (patchValue === undefined) {
      continue;
    }
    if (patchValue === null) {
      delete result[key];
    } else if (typeof patchValue === "object" && !Array.isArray(patchValue)) {
      const currentValue = result[key];
      result[key] = applyJsonMergePatch(currentValue, patchValue);
    } else {
      result[key] = patchValue;
    }
  }
  return result;
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

// function isEmptyObject(v: any): boolean {
//   return typeof v === "object" && v !== null && !Array.isArray(v) && Object.keys(v).length === 0
// }

// function optimize(patch: any): any {
//   if (typeof patch === "object" && patch !== null && !Array.isArray(patch)) {
//     const keys = Object.keys(patch);
//     if (keys.length === 0) {
//       return {};
//     }
//     const result: any = {};
//     for (const key of keys) {
//       const optimized = optimize(patch[key]);
//       if (!isEmptyObject(optimized)) {
//         result[key] = optimized;
//       }
//     }
//     return result;
//   }
//   return patch;
// }

/**
 * Compares two objects. Arrays are compared element-wise.
 * Objects are compared field-wise. In other cases, objects
 * are compared using the "===".
 * 
 * @param a - The first object.
 * @param b - The second object.
 * @returns `true` if objects are equal, else `false`.
 */
function equal(a: any, b: any): boolean {
  if (a === null && b === null) {
    return true;
  }
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.length === b.length && a.every((v, i) => equal(v, b[i]));
  }
  if (typeof a === "object" && typeof b === "object") {
    return Object.keys(a).every((k) => equal(a[k], b[k])) && Object.keys(b).length == Object.keys(a).length;
  }
  return a === b;
}

/**
 * Computes minimal JSON Merge Patch that should be applied to
 * the `source` to transform it into the `target`.
 * 
 * Note: when no patch should be applied, i.e. source and target
 * objects have the same values, `undefined` is returned.
 * 
 * Note: only JSON types are supported plus the function type
 * (this includes classes and functions).
 *  
 * @param source - The source object. 
 * @param target - The target object.
 * @returns JSON Merge Patch.
 */
export function computeJsonMergePatch(source: any, target: any): any {
  if (typeof source === "undefined" || typeof target === "undefined") {
    throw new Error("undefined is not allowed in json merge patch");
  }
  if (source === target) {
    return undefined;
  }
  if (target === null) {
    return null;
  }
  if (source === null) {
    return target;
  }
  const sourceIsObject = typeof source === "object" && source !== null && !Array.isArray(source);
  const targetIsObject = typeof target === "object" && target !== null && !Array.isArray(target);
  if (!sourceIsObject || !targetIsObject) {
    return equal(source, target) ? undefined : target;
  }
  const result: any = {};
  const keys = new Set([...Object.keys(source), ...Object.keys(target)]);
  for (const key of keys) {
    const sourceValue = (source as any)[key];
    const targetValue = (target as any)[key];
    const sourceValueIsUndefined = typeof sourceValue === "undefined";
    const targetValueIsUndefined = typeof targetValue === "undefined";
    if (sourceValueIsUndefined && targetValueIsUndefined) {
      continue;
    }
    if (sourceValueIsUndefined) {
      result[key] = targetValue;
      continue
    }
    if (targetValueIsUndefined) {
      result[key] = null;
      continue
    }
    const patch = computeJsonMergePatch(sourceValue, targetValue);
    if (patch !== undefined) {
      result[key] = patch;
    }
  }
  return Object.keys(result).length === 0 ? undefined : result;
}