export interface PlanEntity {
  id: string;
}

export interface Area extends PlanEntity {
  type: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Furniture extends PlanEntity {
  furnitureId: string;
  x: number;
  y: number;
  z: number;
  yaw: number;
}

export interface PlanPatch {
  name?: string;
  furniture?: Record<string, Partial<Furniture>>;
  areas?: Record<string, Partial<Area>>;
}

export interface PlanContent {
  furniture: Record<string, Furniture>;
  areas: Record<string, Area>;
}

export interface Plan {
  id: string;
  projectId: string;
  name: string;
  content: PlanContent;
  dtCreated: string;
  dtUpdated: string;
  etag: string;
}
