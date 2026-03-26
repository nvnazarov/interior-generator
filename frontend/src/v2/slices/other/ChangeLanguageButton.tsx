import { useCallback } from "react";
import { Button } from "../../shared/components";
import i18next from "i18next";

export function ChangeLanguageButton() {
  const handleClick = useCallback(() => {
    if (i18next.language == "en") {
      i18next.changeLanguage("ru");
    } else {
      i18next.changeLanguage("en");
    }
  }, []);

  return <Button icon="global.png" onClick={handleClick} />;
}
