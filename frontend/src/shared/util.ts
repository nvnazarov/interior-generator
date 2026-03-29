export const UrlUtil = {
  noRightSlash: (url: string): string =>
    url.endsWith("/") ? url.slice(0, url.length - 1) : url,
};
