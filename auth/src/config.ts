const r = (key: string): string => {
  const v = process.env[key];
  if (v === undefined) {
    throw Error(`required env: ${key}`);
  }
  return v;
};

export const config = {
  host: process.env.AUTH__API__HOST || "0.0.0.0",
  port: +(process.env.AUTH__API__PORT || 8080),
  postgres: {
    url:
      `postgresql://${r("AUTH__POSTGRES__USER")}:${r("AUTH__POSTGRES__PASSWORD")}` +
      `@${r("AUTH__POSTGRES__HOST")}:${r("AUTH__POSTGRES__PORT")}` +
      `/${r("AUTH__POSTGRES__DB")}`,
  },
  betterAuth: {
    secret: r("AUTH__BETTER_AUTH__SECRET"),
    baseURL: r("AUTH__BETTER_AUTH__BASE_URL"),
    trustedOrigins: r("AUTH__BETTER_AUTH__TRUSTED_ORIGINS").split(","),
  },
};
