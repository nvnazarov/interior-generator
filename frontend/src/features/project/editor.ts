import type { ProjectPatch } from "./project";

export interface ProjectEditor {
  viewMode: "2d" | "3d";
  zoom: number;
  undo: ProjectChange[];
  redo: ProjectChange[];
  activeTool: "hand" | "wall" | "window" | "door" | "wet_area";
  isDirty: boolean;
  isCatalogOpen: boolean;
  dtLastSaved: string | null;
}

export interface ProjectChange {
  patch: ProjectPatch;
  inversePatch: ProjectPatch;
}
