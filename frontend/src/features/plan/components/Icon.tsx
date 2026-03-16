import { asset } from "../../../shared/util/url";
import "./Icon.scss";

export function Icon({ src }: { src: string }) {
  return <img className="icon" src={asset(src)}></img>;
}
