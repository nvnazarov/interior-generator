import { useEffect } from "react";
import { useAppSelector } from "../../storeTypes";
import { selectPlanEditor } from "../slice";
import { useLazyGetFurnitureByIdQuery } from "../../api/slice";

export function FurniturePreview() {
  const [getFurnitureById, { data, isSuccess }] =
    useLazyGetFurnitureByIdQuery();
  const preview = useAppSelector(
    (state) => selectPlanEditor(state).furniturePreview,
  );
  const furnitureId = preview?.furnitureId;

  useEffect(() => {
    if (furnitureId) {
      getFurnitureById(furnitureId, true);
    }
  }, [furnitureId]);

  if (!preview || !isSuccess) {
    return <></>;
  }

  return (
    <mesh
      position={[preview.x, preview.y, preview.z]}
      rotation={[0, preview.yaw, 0]}
    >
      <boxGeometry args={[data.width, data.height, data.depth]} />
      <meshStandardMaterial color="green" />
    </mesh>
  );
}
