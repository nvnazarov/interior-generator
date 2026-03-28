import { useAppSelector } from "../storeTypes";
import { selectProject } from "./slice";
import { WallMesh } from "./WallMesh";

export function ProjectMesh() {
  const project = useAppSelector(selectProject);
  if (!project) {
    return <></>;
  }
  return (
    <>
      {Object.entries(project.content.walls).map(([id, wall]) => (
        <WallMesh key={id} wall={wall} />
      ))}
    </>
  );
}
