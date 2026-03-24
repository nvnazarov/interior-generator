import { Config } from "./config";
import { UrlUtil } from "./util";

export const Client = {
  createAvatar: async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);
    const resp = await fetch(`${UrlUtil.noRightSlash(Config.gateway.baseUrl)}/api/assets/avatars`, {
      method: 'POST',
      body: formData,
    });
    if (resp.ok) {
      const avatarId = String(await resp.json());
      return avatarId
    }
    throw new Error("failed to create avatar: got status " + resp.status);
  }
}