import { CONFIG } from "../config";

export function withoutTrailingSlash(url: string) {
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

export function withoutLeadingSlash(url: string) {
  return url.startsWith("/") ? url.slice(1) : url;
}

export function withTrailingSlash(url: string) {
  return url.endsWith("/") ? url : url + "/";
}

export function asset(src: string): string {
  return withTrailingSlash(CONFIG.proxy.basePath) + withoutLeadingSlash(src);
}
