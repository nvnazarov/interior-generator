import { useCallback, useState, type ChangeEvent } from "react";
import { useNavigate } from "react-router";
import { authClient } from "../../shared/betterAuth";
import { useAppDispatch } from "../storeTypes";
import { userSignedIn } from "./slice";

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
          // TODO
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
      } catch (e) {
        // TODO
      } finally {
        setIsSigningIn(false);
      }
    },
    [email, password, isSigningIn],
  );

  return (
    <form>
      <input value={email} onChange={handleEmailChange} />
      <input value={password} onChange={handlePasswordChange} />
      <button onClick={handleSignIn} disabled={isSigningIn}>
        Sign In
      </button>
    </form>
  );
}
