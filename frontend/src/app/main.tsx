import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { RouterProvider } from "react-router";

import "../styles/global.scss";
import "../shared/i18n";
import { store } from "../slices/store";
import { router } from "./router";
import { NotificationPopup } from "../slices/notifications/NotificationPopup";

const container = document.getElementById("root")!;
const root = createRoot(container);

root.render(
  <StrictMode>
    <Provider store={store}>
      <RouterProvider router={router} />
      <NotificationPopup />
    </Provider>
  </StrictMode>,
);
