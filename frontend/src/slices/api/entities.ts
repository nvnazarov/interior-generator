export interface Wall {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Window {
  id: string;
  wallId: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Door {
  id: string;
  wallId: string;
  x: number;
  w: number;
  h: number;
}

export interface WetArea {
  id: string;
  points: { x: number, y: number }[]
}

export interface Project {
  id: string;
  accountId: string;
  name: string;
  description: string;
  published: boolean;
  content: {
    walls: Record<string, Wall>;
    windows: Record<string, Window>;
    doors: Record<string, Door>;
    wetAreas: Record<string, WetArea>;
  };
  revision: string;
  dtCreated: string;
  dtUpdated: string;
}

export interface ProjectPatch {
  name?: string;
  description?: string;
  content?: {
    walls?: Record<string, Partial<Wall> | null>;
    windows?: Record<string, Partial<Window> | null>;
    doors?: Record<string, Partial<Door> | null>;
    wetAreas?: Record<string, Partial<WetArea> | null>;
  };
}

export interface FunctionalArea {
  id: string;
  type: "kitchen" | "livingroom" | "bedroom" | "bathroom" | "hallway";
  points: { x: number, y: number }[]
}

export interface FurnitureInPlan {
  id: string;
  furnitureId: string;
  x: number;
  y: number;
  z: number;
  yaw: number;
}

export interface PlanPatch {
  name?: string;
  content?: {
    furniture?: Record<string, Partial<FurnitureInPlan> | null>;
    areas?: Record<string, Partial<FunctionalArea> | null>;
  }
}

export interface Plan {
  id: string;
  projectId: string;
  name: string;
  content: {
    furniture: Record<string, FurnitureInPlan>;
    areas: Record<string, FunctionalArea>;
  };
  revision: string;
  dtCreated: string;
  dtUpdated: string;
}

export interface Furniture {
  id: string;
  name: string;
  width: number;
  height: number;
  depth: number;
  modelPath: string;
  thumbnailPath: string;
  iconPath: string;
  mount: string;
  meta: Record<string, any>;
}
