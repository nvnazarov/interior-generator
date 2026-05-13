import { useCallback, useState, type ChangeEvent } from "react";
import { Link, useNavigate } from "react-router";

import "./SignInForm.scss";
import { authClient } from "../../../../shared/betterAuth";
import { useAppDispatch } from "../../../storeTypes";
import { userSignedIn } from "../../slice";
import { notify } from "../../../notifications/slice";
import { TextInput } from "../../../../shared/components/input/TextInput";
import { Button } from "../../../../shared/components/button/Button";

export function SignInForm() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSigningIn, setIsSigningIn] = useState(false);

  const handleEmailChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  }, []);

  const handlePasswordChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setPassword(e.target.value);
    },
    [],
  );

  const handleSignIn = useCallback(
    async (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
      e.preventDefault();
      if (isSigningIn) {
        return;
      }
      try {
        setIsSigningIn(true);
        const result = await authClient.signIn.email({ email, password });
        if (result.error) {
          dispatch(notify({ text: result.error.message, severity: "error" }));
          return;
        }
        const data = result.data;
        dispatch(
          userSignedIn({
            id: data.user.id,
            name: data.user.name,
            email: data.user.email,
            avatarUrl: data.user.image || null,
            dtCreated: data.user.createdAt.toISOString(),
          }),
        );
        navigate("/profile");
      } catch {
        dispatch(notify({ text: "Unable to sign you in", severity: "error" }));
      } finally {
        setIsSigningIn(false);
      }
    },
    [email, password, isSigningIn],
  );

  return (
    <form className="sign-in-form">
      <p>
        Do not have an account? <Link to="/sign-up">Sign up</Link>
      </p>
      <TextInput
        value={email}
        onChange={handleEmailChange}
        placeholder="Email"
      />
      <TextInput
        value={password}
        onChange={handlePasswordChange}
        placeholder="Password"
      />
      <Button
        onClick={handleSignIn}
        disabled={isSigningIn}
        primary
        text="Sign in"
      />
    </form>
  );
}
