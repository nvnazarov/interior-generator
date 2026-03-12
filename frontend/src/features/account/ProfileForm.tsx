import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { authClient, selectData } from "./accountSlice";
import "./ProfileForm.scss";
import { useNavigate } from "react-router";

export function ProfileForm() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [busy, setBusy] = useState(false);
  const [name, setName] = useState("");
  const data = useAppSelector(selectData);

  useEffect(() => {
    if (!data) {
      navigate("/sign-in");
    } else {
      setName(data.name);
    }
  }, [useAppSelector, data]);

  function handleSubmit(e: React.MouseEvent<HTMLButtonElement, MouseEvent>) {
    e.preventDefault();
    if (!busy) {
      setBusy(true);
      // TODO
    }
  }

  return (
    <form className="profile-form">
      <p>This is your profile</p>
      <input
        type="text"
        placeholder="name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        type="text"
        placeholder="email"
        value={data?.email || ""}
        disabled={true}
      />
      <button type="submit" onClick={(e) => handleSubmit(e)}>
        Save
      </button>
    </form>
  );
}
