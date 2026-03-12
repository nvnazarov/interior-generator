import React, { useState } from "react";
import { signIn, type SignInError } from "./accountSlice";
import { useAppDispatch } from "../../app/hooks";
import { Link, useNavigate } from "react-router";
import "./SignInForm.scss";

export function SignInForm() {
  const dispatch = useAppDispatch();
  const [busy, setBusy] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<SignInError | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();
    try {
      setError(null);
      setBusy(true);
      await dispatch(signIn({ email, password })).unwrap();
      navigate("/profile");
    } catch (e) {
      setError(e as SignInError);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="sign-in-form">
      <p>Sign in to use the app</p>
      <input
        type="text"
        placeholder="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="text"
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && (
        <div>
          {error.code == "INCORRECT_EMAIL_OR_PASSWORD" &&
            "incorrect email or password"}
          {error.code == "INVALID_EMAIL" && "invalid email"}
          {error.code == "OTHER" && "unknown error"}
        </div>
      )}

      <button type="submit" onClick={(e) => handleSubmit(e)} disabled={busy}>
        Sign In
      </button>
      <Link to="/sign-up">Sign up instead</Link>
    </form>
  );
}
