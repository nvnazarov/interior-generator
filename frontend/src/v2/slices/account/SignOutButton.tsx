import { useCallback, useState } from "react";
import { useAppDispatch } from "../storeTypes";
import { authClient } from "../../shared/betterAuth";
import { userSignedOut } from "./slice";
import { useNavigate } from "react-router";

export function SignOutButton() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [isSigningOut, setIsSigningOut] = useState(false);

  const handleSignOut = useCallback(async () => {
    if (isSigningOut) {
      return;
    }
    try {
      setIsSigningOut(true);
      await authClient.signOut();
      dispatch(userSignedOut());
      navigate("/sign-in");
    } finally {
      setIsSigningOut(false);
    }
  }, [isSigningOut]);

  return (
    <button onClick={handleSignOut} disabled={isSigningOut}>
      Sign Out
    </button>
  );
}
