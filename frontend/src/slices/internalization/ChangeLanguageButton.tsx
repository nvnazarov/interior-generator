import { useState } from "react";
import i18next from "i18next";
import { Button } from "../../shared/components/button/Button";
import { LANGUAGES } from "../../shared/i18n";

export function ChangeLanguageButton() {
  const [language, setLanguage] = useState(i18next.language);

  function handleClick() {
    const index = LANGUAGES.indexOf(language);
    const targetLanguage = LANGUAGES[(index + 1) % LANGUAGES.length]!;
    i18next.changeLanguage(targetLanguage);
    setLanguage(targetLanguage);
  }

  return (
    <Button
      icon="global.png"
      onClick={handleClick}
      text={language.toUpperCase()}
    />
  );
}
