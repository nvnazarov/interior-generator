import { CONFIG } from "../config";

export const AssetsClient = {
  icon: (path: string): string => CONFIG.gateway.baseURL + path,
  thumbnail: (path: string): string => CONFIG.gateway.baseURL + path,
};
