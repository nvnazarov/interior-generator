import "dotenv/config";

const r = (key: string): string => {
  const v = process.env[key];
  if (v === undefined) {
    throw Error(`required env: ${key}`);
  }
  return v;
};

export const config = {
  port: process.env.APP_PORT || "8080",
  postgres: {
    url: r("APP_POSTGRES__URL"),
  },
  betterAuth: {
    baseURL: r("BETTER_AUTH_BASE_URL"),
    trustedOrigins: r("BETTER_AUTH_TRUSTED_ORIGINS").split(","),
  },
};
