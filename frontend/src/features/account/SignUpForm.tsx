import React, { useState } from "react";
import "./SignUpForm.scss";
import { Link, useNavigate } from "react-router";
import { signUp, type SignUpError } from "./accountSlice";
import { useAppDispatch } from "../../app/hooks";

export function SignUpForm() {
  const dispatch = useAppDispatch();
  const [busy, setBusy] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<SignUpError | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();
    try {
      setError(null);
      setBusy(true);
      await dispatch(signUp({ name, email, password })).unwrap();
      navigate("/profile");
    } catch (e) {
      setError(e as SignUpError);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="sign-up-form">
      <p>Sign up to use the app</p>
      <input
        type="text"
        placeholder="name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
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
          {error.code == "VALIDATION_ERROR" && "invalid data"}
          {error.code == "USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL" &&
            "user already exists"}
          {error.code == "PASSWORD_TOO_SHORT" && "password too short"}
          {error.code == "OTHER" && "unknown error"}
        </div>
      )}
      <button type="submit" onClick={(e) => handleSubmit(e)} disabled={busy}>
        Sign up
      </button>
      <Link to="/sign-in">Sign in instead</Link>
    </form>
  );
}
