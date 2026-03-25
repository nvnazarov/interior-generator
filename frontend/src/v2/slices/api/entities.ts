export interface Project {
  id: string;
  accountId: string;
  name: string;
  description: string;
  published: boolean;
  content: {
    walls: Record<
      string,
      {
        x1: number;
        y1: number;
        x2: number;
        y2: number;
      }
    >;
    windows: Record<
      string,
      {
        wallId: string;
        x: number;
        y: number;
        w: number;
        h: number;
      }
    >;
    doors: Record<
      string,
      {
        wallId: string;
        x: number;
        w: number;
        h: number;
      }
    >;
    wetAreas: Record<
      string,
      {
        x: number;
        y: number;
        w: number;
        h: number;
      }
    >;
  };
  revision: string;
  dtCreated: string;
  dtUpdated: string;
}
