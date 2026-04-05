import "./Hint.scss";
import { useAppSelector } from "../storeTypes";
import { selectHint } from "./slice";
import { useEffect, useState, type CSSProperties } from "react";

export function Hint() {
  const hint = useAppSelector(selectHint);
  const [hidden, setHidden] = useState(true);

  useEffect(() => {
    if (hint.hidden) {
      setHidden(true);
    } else {
      const timer = setTimeout(() => setHidden(false), 500);
      return () => {
        clearTimeout(timer);
      };
    }
  }, [hint.hidden]);

  if (hidden) {
    return <></>;
  }
  const style: CSSProperties = {
    top: hint.y || "20px",
    left: hint.x || "20px",
  };
  return (
    <div className="plan-editor__hint" style={style}>
      <span>{hint.title}</span>
      {hint.description && <span>{hint.description}</span>}
      {hint.length && <span>Длина: {hint.length}м</span>}
    </div>
  );
}
