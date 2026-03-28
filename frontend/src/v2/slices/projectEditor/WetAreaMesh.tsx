import { Plane } from "@react-three/drei";
import type { WetArea } from "../api/entities";
import * as THREE from "three";

const WET_AREA_MATERIAL = new THREE.MeshStandardMaterial({
  color: "lightblue",
});

export function WetAreaMesh({ wetArea }: { wetArea: WetArea }) {
  const size = new THREE.Vector3(wetArea.w, 0, wetArea.h);
  const corner = new THREE.Vector3(wetArea.x, 0, wetArea.y);
  const center = new THREE.Vector3().add(size).multiplyScalar(0.5).add(corner);
  return (
    <Plane
      args={[size.x, size.z]}
      position={center}
      rotation={[-Math.PI / 2, 0, 0]}
      material={WET_AREA_MATERIAL}
    />
  );
}
