export interface ProjectEntity {
  id: string;
}

export interface WetArea extends ProjectEntity {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Door extends ProjectEntity {
  wallId: string;
  x: number;
  w: number;
  h: number;
}

export interface Window extends ProjectEntity {
  wallId: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Wall extends ProjectEntity {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface ProjectPatch {
  name?: string;
  description?: string;
  content?: {
    walls?: Record<string, Partial<Wall> | null>;
    windows?: Record<string, Partial<Window> | null>;
    doors?: Record<string, Partial<Door> | null>;
    wetAreas?: Record<string, Partial<WetArea> | null>;
  }
}

export interface ProjectContent {
  walls: Record<string, Wall>;
  windows: Record<string, Window>;
  doors: Record<string, Door>;
  wetAreas: Record<string, WetArea>;
}

export interface Project {
  id: string;
  accountId: string;
  name: string;
  description: string;
  published: boolean;
  content: ProjectContent;
  dtCreated: string;
  dtUpdated: string;
  etag: string;
}

function applyJsonMergePatch<T>(target: T, patch: any): T {
  if (patch === null || typeof patch !== 'object' || Array.isArray(patch)) {
    return patch as T;
  }
  const result: any = target !== null && typeof target === 'object' && !Array.isArray(target)
    ? { ...target }
    : {};
  for (const key of Object.keys(patch)) {
    const patchValue = patch[key];
    if (patchValue === null) {
      delete result[key];
    }
    else if (typeof patchValue === 'object' && !Array.isArray(patchValue)) {
      const currentValue = result[key];
      result[key] = applyJsonMergePatch(currentValue, patchValue);
    }
    else {
      result[key] = patchValue;
    }
  }
  return result as T;
}

function mergePatchObjects(target: any, source: any): any {
  const result = { ...target };
  for (const key of Object.keys(source)) {
    const sourceValue = source[key];
    if (sourceValue === null) {
      result[key] = null;
    }
    else if (
      typeof sourceValue === 'object' &&
      !Array.isArray(sourceValue) &&
      typeof result[key] === 'object' &&
      !Array.isArray(result[key]) &&
      result[key] !== null
    ) {
      result[key] = mergePatchObjects(result[key], sourceValue);
    }
    else {
      result[key] = sourceValue;
    }
  }
  return result;
}


export const ProjectUtils = {
  isEmpty(project: Project): boolean {
    return (
      Object.keys(project.content.doors).length === 0 &&
      Object.keys(project.content.walls).length === 0 &&
      Object.keys(project.content.windows).length === 0 &&
      Object.keys(project.content.wetAreas).length === 0
    );
  },
  applyPatch(project: Project, patch: ProjectPatch): Project {
    return applyJsonMergePatch(project, patch)
  },
  mergePatches(patches: ProjectPatch[]): ProjectPatch {
    if (patches.length === 0) return {};
    if (patches.length === 1) return patches[0]!;
    let result: any = {};
    for (const patch of patches) {
      if (patch === null) {
        result = null;
        continue;
      }
      if (result === null) {
        continue;
      }
      if (typeof patch !== 'object' || Array.isArray(patch)) {
        result = patch;
        continue;
      }
      result = mergePatchObjects(result, patch);
    }
    return result;
  }
};
