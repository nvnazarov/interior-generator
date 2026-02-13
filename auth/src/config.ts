export class PostgresConfig {
  constructor(
    public host: string,
    public port: string,
    public db: string,
    public user: string,
    public password: string,
  ) {}

  public uri(): string {
    return `postgres://${this.user}:${this.password}@${this.host}:${this.port}/${this.db}`;
  }
}

export type BetterAuthConfig = {
  baseURL: string;
  trustedOrigins: string[];
};

export type Config = {
  port: string;
  betterAuth: BetterAuthConfig;
  postgres: PostgresConfig;
};

export function loadConfigFromEnv(): Config {
  const r = (key: string): string => {
    const v = process.env[key];
    if (v === undefined) {
      throw Error(`required env: ${key}`);
    }
    return v;
  };

  return {
    port: process.env.APP_PORT || "8080",
    postgres: new PostgresConfig(
      r("APP_POSTGRES__HOST"),
      r("APP_POSTGRES__PORT"),
      r("APP_POSTGRES__DB"),
      r("APP_POSTGRES__USER"),
      r("APP_POSTGRES__PASSWORD"),
    ),
    betterAuth: {
      baseURL: r("BETTER_AUTH_BASE_URL"),
      trustedOrigins: r("BETTER_AUTH_TRUSTED_ORIGINS").split(","),
    },
  };
}
