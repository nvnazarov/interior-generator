import { useCallback, useState, type ChangeEvent } from "react";
import { Link, useNavigate } from "react-router";

import "./SignUpForm.scss";
import { authClient } from "../../../../shared/betterAuth";
import { useAppDispatch } from "../../../storeTypes";
import { userSignedUp } from "../../slice";
import { notify } from "../../../notifications/slice";
import { TextInput } from "../../../../shared/components/input/TextInput";
import { Button } from "../../../../shared/components/button/Button";

export function SignUpForm() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSigningUp, setIsSigningUp] = useState(false);

  const handleNameChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  }, []);

  const handleEmailChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  }, []);

  const handlePasswordChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setPassword(e.target.value);
    },
    [],
  );

  const handleSignUp = useCallback(
    async (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
      e.preventDefault();
      if (isSigningUp) {
        return;
      }
      try {
        setIsSigningUp(true);
        const result = await authClient.signUp.email({ name, email, password });
        if (result.error) {
          dispatch(notify({ text: result.error.message, severity: "error" }));
          return;
        }
        const data = result.data;
        dispatch(
          userSignedUp({
            id: data.user.id,
            name: data.user.name,
            email: data.user.email,
            avatarUrl: data.user.image || null,
            dtCreated: data.user.createdAt.toISOString(),
          }),
        );
        navigate("/profile");
      } catch {
        dispatch(notify({ text: "Unable to sign you up", severity: "error" }));
      } finally {
        setIsSigningUp(false);
      }
    },
    [name, email, password, isSigningUp],
  );

  return (
    <form className="sign-up-form">
      <p>
        Already have an account? <Link to="/sign-in">Sign in</Link>
      </p>
      <TextInput value={name} onChange={handleNameChange} placeholder="Name" />
      <TextInput
        value={email}
        onChange={handleEmailChange}
        placeholder="Email"
      />
      <TextInput
        type="password"
        value={password}
        onChange={handlePasswordChange}
        placeholder="Password"
      />
      <Button
        onClick={handleSignUp}
        loading={isSigningUp}
        primary
        text="Sign up"
      />
    </form>
  );
}
