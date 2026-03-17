import type { Project, ProjectPatch } from "./project";

export interface ProjectEditor {
  viewMode: "2d" | "3d";
  undo: ProjectChange[];
  redo: ProjectChange[];
  sync: ProjectPatch[];
  activeTool: "hand" | "wall" | "window" | "door" | "wet_area";
  dtLastSaved: string;
  project: Project | null;
}

export interface ProjectChange {
  patch: ProjectPatch;
  inversePatch: ProjectPatch;
}
