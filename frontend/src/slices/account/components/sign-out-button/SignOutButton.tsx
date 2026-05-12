import { useCallback, useState } from "react";
import { useNavigate } from "react-router";

import { useAppDispatch } from "../../../storeTypes";
import { authClient } from "../../../../shared/betterAuth";
import { userSignedOut } from "../../slice";
import { Button } from "../../../../shared/components/button/Button";

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

  return <Button onClick={handleSignOut} text="Sign out" />;
}
