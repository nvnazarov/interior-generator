import { useState } from "react";
import i18next from "i18next";
import { Button } from "../../shared/components/button/Button";
import { LANGUAGES } from "../../shared/i18n";
import { useAppDispatch } from "../storeTypes";
import { notify } from "../notifications/slice";

export function ChangeLanguageButton() {
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState(i18next.language);

  async function handleClick() {
    if (loading) return;
    try {
      setLoading(true);
      const index = LANGUAGES.indexOf(language);
      const targetLanguage = LANGUAGES[(index + 1) % LANGUAGES.length]!;
      await i18next.changeLanguage(targetLanguage);
      setLanguage(targetLanguage);
    } catch {
      dispatch(
        notify({ text: "Unable to switch language", severity: "error" }),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <Button
      icon="global.png"
      onClick={handleClick}
      loading={loading}
      disabled={loading}
      text={language.toUpperCase()}
    />
  );
}
