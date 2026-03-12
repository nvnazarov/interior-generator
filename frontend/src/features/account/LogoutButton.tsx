import type React from "react";
import { useAppDispatch } from "../../app/hooks";
import { signOut } from "./accountSlice";
import { useNavigate } from "react-router";
import { useState } from "react";

export function LogoutButton() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [busy, setBusy] = useState(false);

  const handleClick = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();
    try {
      setBusy(true);
      await dispatch(signOut()).unwrap();
      navigate("/sign-in");
    } catch (e) {
      navigate("/sign-in");
    } finally {
      setBusy(false);
    }
  };

  return (
    <button onClick={(e) => handleClick(e)} disabled={busy}>
      Sign out
    </button>
  );
}
