import * as THREE from "three";

import { type Wall } from "../../api/entities";
import { CM, M } from "../lib";
import { MeshMenu } from "../../../shared/components";

export function WallMesh({ wall }: { wall: Wall }) {
  const start = new THREE.Vector3(wall.x1, 0, wall.y1);
  const end = new THREE.Vector3(wall.x2, 0, wall.y2);
  const length = start.distanceTo(end) + 20 * CM;
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start).normalize();
  const angle = Math.atan2(direction.z, direction.x);

  return (
    <MeshMenu
      hint={
        <>
          Wall
          <br />
          <br /> <b>Length:</b> {Math.round(length - 20 * CM) / M}m
        </>
      }
    >
      <mesh
        position={[center.x, (3 * M) / 2, center.z]}
        rotation={[0, -angle, 0]}
      >
        <boxGeometry args={[length, 3 * M, 20 * CM]} />
        <meshStandardMaterial color="white" />
      </mesh>
    </MeshMenu>
  );
}
