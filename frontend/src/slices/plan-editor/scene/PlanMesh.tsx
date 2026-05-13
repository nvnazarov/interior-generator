import { useEffect } from "react";

import { useLazyGetProjectByIdQuery } from "../../api/slice";
import { useAppSelector } from "../../storeTypes";
import { DoorMesh } from "./DoorMesh";
import { selectPlan } from "../slice";
import { WallMesh } from "./WallMesh";
import { WindowMesh } from "./WindowMesh";
import { AreaMesh } from "./AreaMesh";
import { FurnitureMesh } from "./FurnitureMesh";

export function PlanMesh() {
  const plan = useAppSelector(selectPlan);
  const [getProjectById, { data, error }] = useLazyGetProjectByIdQuery();

  useEffect(() => {
    async function loadProject(id: string) {
      await getProjectById(id, true).unwrap();
    }
    if (plan) {
      loadProject(plan.projectId);
    }
  }, [plan?.projectId]);

  if (!plan || !data || error) {
    return <></>;
  }

  return (
    <>
      {Object.entries(data.content.walls).map(([id, wall]) => (
        <WallMesh key={id} wall={wall} />
      ))}
      {Object.entries(data.content.windows).map(([id, window]) => {
        const wall = data.content.walls[window.wallId];
        if (!wall) {
          return <></>;
        } else {
          return <WindowMesh key={id} window={window} wall={wall} />;
        }
      })}
      {Object.entries(data.content.doors).map(([id, door]) => {
        const wall = data.content.walls[door.wallId];
        if (!wall) {
          return <></>;
        } else {
          return <DoorMesh key={id} door={door} wall={wall} />;
        }
      })}
      {Object.entries(plan.content.areas).map(([id, area]) => (
        <AreaMesh key={id} area={{ id, ...area }} />
      ))}
      {Object.entries(plan.content.furniture).map(([id, furniture]) => (
        <FurnitureMesh key={id} furniture={{ id, ...furniture }} />
      ))}
    </>
  );
}
