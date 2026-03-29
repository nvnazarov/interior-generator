import i18next from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";
import Backend from "i18next-http-backend";

i18next
  .use(LanguageDetector)
  .use(initReactI18next)
  .use(new Backend(undefined, { loadPath: "/app/locales/{{lng}}/{{ns}}.json" }))
  .init({
    returnObjects: true,
    fallbackLng: "en",
  });
