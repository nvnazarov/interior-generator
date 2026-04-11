import { useCallback, useState } from "react";
import { useAppDispatch } from "../storeTypes";
import { authClient } from "../../shared/betterAuth";
import { userSignedOut } from "./slice";
import { useNavigate } from "react-router";
import { Button } from "../../shared/components";

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
      const result = await authClient.signOut();
      if (result.error) {
        // Ignore the error.
      }
      dispatch(userSignedOut());
      navigate("/sign-in");
    } finally {
      setIsSigningOut(false);
    }
  }, [isSigningOut]);

  return (
    <Button
      icon="signout.png"
      onClick={handleSignOut}
      disabled={isSigningOut}
    />
  );
}
