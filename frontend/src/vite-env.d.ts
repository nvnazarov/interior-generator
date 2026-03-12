interface ImportMetaEnv {
  readonly FRONTEND__API_GATEWAY__BASE_URL: string
  readonly FRONTEND__PROXY__BASE_PATH: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}