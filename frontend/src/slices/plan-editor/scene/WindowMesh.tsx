import * as THREE from "three";
import type { Wall, Window } from "../../api/entities";
import { CM, M } from "../lib";
import { MeshMenu } from "../../../shared/components";

export function WindowMesh({ window, wall }: { window: Window; wall: Wall }) {
  const wallStart = new THREE.Vector3(wall.x1, 0, wall.y1);
  const wallEnd = new THREE.Vector3(wall.x2, 0, wall.y2);
  const direction = new THREE.Vector3()
    .subVectors(wallEnd, wallStart)
    .normalize();
  const start = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(window.x));
  const end = wallStart
    .clone()
    .add(direction.clone().multiplyScalar(window.x + window.w));
  const length = start.distanceTo(end);
  const center = new THREE.Vector3();
  center.addVectors(start, end).multiplyScalar(0.5);
  const angle = Math.atan2(direction.z, direction.x);

  return (
    <MeshMenu
      hint={
        <>
          Window
          <br />
          <br />
          <b>Width:</b> {window.w / M} m<br />
          <b>Height:</b> {window.h / M} m
        </>
      }
    >
      <mesh
        position={[center.x, window.y + window.h / 2, center.z]}
        rotation={[0, -angle, 0]}
      >
        <boxGeometry args={[length, window.h, 24 * CM]} />
        <meshStandardMaterial color="blue" />
      </mesh>
    </MeshMenu>
  );
}
