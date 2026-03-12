import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import "./PlanViewer.scss";

type ViewerContext = {
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  renderer: THREE.WebGLRenderer;
};

export const PlanViewer = () => {
  const windowRef = useRef<HTMLDivElement>(null);
  const [_, setCtx] = useState<ViewerContext | null>(null);

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    setCtx({ scene, camera, renderer });

    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    camera.translateZ(5);
    renderer.setClearColor("white");

    // Capture windowRef.current to use it in clean up later.
    const mount = windowRef.current;

    if (mount) {
      mount.appendChild(renderer.domElement);
    }

    const render = () => {
      renderer.render(scene, camera);
    };

    const resizeObserver = new ResizeObserver(() => {
      if (!mount) return;
      const { clientWidth, clientHeight } = mount;
      renderer.setSize(clientWidth, clientHeight);
      camera.aspect = clientWidth / clientHeight;
      camera.updateProjectionMatrix();
      render();
    });

    if (mount) resizeObserver.observe(mount);

    render();

    return () => {
      resizeObserver.disconnect();
      renderer.dispose();
      mount?.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      className="plan-viewer"
      onClick={() => windowRef.current?.requestFullscreen()}
      ref={windowRef}
    ></div>
  );
};
