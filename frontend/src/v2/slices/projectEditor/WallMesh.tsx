const WALL_HEIGHT = 600;

export function WallMesh() {
  return (
    <mesh
      position={[center.x, WALL_HEIGHT / 2, center.z]}
      rotation={[0, -angle, 0]}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerLeave}
    >
      <boxGeometry args={[length, WALL_HEIGHT, WALL_DEPTH]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "white"} />
    </mesh>
  );
}
