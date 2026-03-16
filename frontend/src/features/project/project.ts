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
  walls?: Record<string, Partial<Wall>>;
  windows?: Record<string, Partial<Window>>;
  doors?: Record<string, Partial<Door>>;
  wetAreas?: Record<string, Partial<WetArea>>;
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
  wallLength(wall: Wall): number {
    return Math.hypot(wall.x1 - wall.x2, wall.y1 - wall.y2);
  },
};
