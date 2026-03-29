import { useCallback, useState, type ChangeEvent } from "react";
import { useNavigate } from "react-router";
import { authClient } from "../../shared/betterAuth";
import { useAppDispatch } from "../storeTypes";
import { userSignedUp } from "./slice";

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
          // TODO
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
      } catch (e) {
        // TODO
      } finally {
        setIsSigningUp(false);
      }
    },
    [name, email, password, isSigningUp],
  );

  return (
    <form>
      <input value={name} onChange={handleNameChange} />
      <input value={email} onChange={handleEmailChange} />
      <input value={password} onChange={handlePasswordChange} />
      <button onClick={handleSignUp} disabled={isSigningUp}>
        Sign Up
      </button>
    </form>
  );
}
