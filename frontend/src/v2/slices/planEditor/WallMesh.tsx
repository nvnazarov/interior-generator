import type { Wall } from "../api/entities";
import * as THREE from "three";
import { CM, M } from "./lib";

export function WallMesh({ wall }: { wall: Wall }) {
  const start = new THREE.Vector3(wall.x1, 0, wall.y1);
  const end = new THREE.Vector3(wall.x2, 0, wall.y2);
  const length = start.distanceTo(end) + 20 * CM;
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start).normalize();
  const angle = Math.atan2(direction.z, direction.x);

  return (
    <>
      <mesh
        position={[center.x, (3 * M) / 2, center.z]}
        rotation={[0, -angle, 0]}
      >
        <boxGeometry args={[length, 3 * M, 20 * CM]} />
        <meshStandardMaterial color="white" />
      </mesh>
    </>
  );
}
