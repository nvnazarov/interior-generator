import { useAppSelector } from "../../storeTypes";
import { DoorMesh } from "./DoorMesh";
import { selectProject } from "../slice";
import { WallMesh } from "./WallMesh";
import { WetAreaMesh } from "./WetAreaMesh";
import { WindowMesh } from "./WindowMesh";

export function ProjectMesh() {
  const project = useAppSelector(selectProject);
  if (!project) {
    return <></>;
  }
  return (
    <>
      {Object.entries(project.content.walls).map(([id, wall]) => (
        <WallMesh key={id} wall={{ id, ...wall }} />
      ))}
      {Object.entries(project.content.wetAreas).map(([id, wetArea]) => (
        <WetAreaMesh key={id} area={{ id, ...wetArea }} />
      ))}
      {Object.entries(project.content.windows).map(([id, window]) => {
        const wall = project.content.walls[window.wallId];
        if (!wall) {
          return <></>;
        } else {
          return <WindowMesh key={id} window={{ id, ...window }} wall={wall} />;
        }
      })}
      {Object.entries(project.content.doors).map(([id, door]) => {
        const wall = project.content.walls[door.wallId];
        if (!wall) {
          return <></>;
        } else {
          return <DoorMesh key={id} door={{ id, ...door }} wall={wall} />;
        }
      })}
    </>
  );
}
