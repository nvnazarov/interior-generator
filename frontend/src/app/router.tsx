import { createBrowserRouter, Navigate, useNavigation } from "react-router";
import { Config } from "../shared/config";
import { UrlUtil } from "../shared/util";
import {
  ProjectEditorPage,
  HomePage,
  ProfilePage,
  SignInPage,
  SignUpPage,
  PlanEditorPage,
} from "../pages";
import { authClient } from "../shared/betterAuth";
import { Outlet } from "react-router";
import { store } from "../slices/store";
import { accountRestored, selectMyAccount } from "../slices/account/slice";
import { useAppSelector } from "../slices/storeTypes";

async function loadSessionIfExists() {
  if (store.getState().account) {
    return;
  }
  const { data } = await authClient.getSession();
  if (data) {
    store.dispatch(
      accountRestored({
        id: data.user.id,
        name: data.user.name,
        email: data.user.email,
        avatarUrl: data.user.image || null,
        dtCreated: data.user.createdAt.toISOString(),
      }),
    );
  }
}

function ProtectedRoute() {
  const account = useAppSelector(selectMyAccount);
  if (account === null) {
    return <Navigate to="/sign-in" replace />;
  }
  return <Outlet />;
}

function SessionLoader() {
  const navigation = useNavigation();
  const isNavigating = Boolean(navigation.location);
  if (isNavigating) {
    return <>Loading</>;
  }
  return <Outlet />;
}

export const router = createBrowserRouter(
  [
    {
      path: "/",
      Component: SessionLoader,
      loader: loadSessionIfExists,
      children: [
        {
          element: <ProtectedRoute />,
          children: [
            {
              path: "/",
              element: <HomePage />,
            },
            {
              path: "/profile",
              element: <ProfilePage />,
            },
            {
              path: "/editor/project/:projectId",
              element: <ProjectEditorPage />,
            },
            {
              path: "/editor/project/:projectId/plan/:planId",
              element: <PlanEditorPage />,
            },
          ],
        },
      ],
    },
    {
      path: "/sign-in",
      element: <SignInPage />,
    },
    {
      path: "/sign-up",
      element: <SignUpPage />,
    },
    {
      path: "*",
      element: <Navigate to="/" />,
    },
  ],
  { basename: UrlUtil.noRightSlash(Config.proxy.basePath) },
);
