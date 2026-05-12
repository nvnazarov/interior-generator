import * as THREE from "three";
import type { Door, Wall } from "../../api/entities";
import { CM, M } from "../lib";
import { MeshMenu } from "../../../shared/components";

export function DoorMesh({ door, wall }: { door: Door; wall: Wall }) {
  const wallStart = new THREE.Vector3(wall.x1, 0, wall.y1);
  const wallEnd = new THREE.Vector3(wall.x2, 0, wall.y2);
  const direction = new THREE.Vector3()
    .subVectors(wallEnd, wallStart)
    .normalize();
  const start = wallStart.clone().add(direction.clone().multiplyScalar(door.x));
  const end = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(door.x + door.w));
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const angle = Math.atan2(direction.z, direction.x);

  return (
    <MeshMenu
      hint={
        <>
          Door
          <br />
          <br />
          <b>Width:</b> {door.w / M} m<br />
          <b>Height:</b> {door.h / M} m
        </>
      }
    >
      <mesh
        position={[center.x, door.h / 2, center.z]}
        rotation={[0, -angle, 0]}
      >
        <boxGeometry args={[length, door.h, 24 * CM]} />
        <meshStandardMaterial color="brown" />
      </mesh>
    </MeshMenu>
  );
}
