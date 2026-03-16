import { createBrowserRouter, Navigate } from "react-router";
import { SignIn } from "../pages/sign-in";
import { Profile } from "../pages/profile";
import { SignUp } from "../pages/sign-up";
import { Projects } from "../pages/projects";
import { Project } from "../pages/project";
import { CONFIG } from "../shared/config";
import { withoutTrailingSlash } from "../shared/util/url";

export const router = createBrowserRouter(
  [
    {
      path: "/projects",
      element: <Projects />,
    },
    {
      path: "/projects/:id",
      element: <Project />,
    },
    {
      path: "/profile",
      element: <Profile />,
    },
    {
      path: "/sign-in",
      element: <SignIn />,
    },
    {
      path: "/sign-up",
      element: <SignUp />,
    },
    {
      path: "*",
      element: <Navigate to="/sign-in" />,
    },
  ],
  { basename: withoutTrailingSlash(CONFIG.proxy.basePath) },
);
