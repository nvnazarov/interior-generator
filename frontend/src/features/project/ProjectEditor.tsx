import { useEffect, useRef, type ChangeEvent } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {
  fetchProject,
  optimisticPatchProject,
  selectProjectById,
  type Project,
} from "./projectSlice";
import * as THREE from "three";
import "./ProjectEditor.scss";
import { FurnitureCatalog } from "../furniture/FurnitureCatalog";
import { PlanEditor } from "../plan/PlanEditor";

export interface Props {
  id: string;
}

function Editor({ id }: { id: string }) {
  const project = useAppSelector(selectProjectById(id));
  const sceneRef = useRef<THREE.Scene>(null);
  const cameraRef = useRef<THREE.Camera>(null);
  const rendererRef = useRef<THREE.WebGLRenderer>(null);
  const canvasContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvasContainer = canvasContainerRef.current;
    if (canvasContainer === null) {
      return;
    }

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#aaa");
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 2000);
    const renderer = new THREE.WebGLRenderer();

    canvasContainer.appendChild(renderer.domElement);

    renderer.setAnimationLoop(() => renderer.render(scene, camera));

    camera.position.z = 5;

    const resizeObserver = new ResizeObserver(() => {
      const { clientWidth, clientHeight } = canvasContainer;
      renderer.setSize(clientWidth, clientHeight);
    });

    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;

    return () => {
      canvasContainer.removeChild(renderer.domElement);
      resizeObserver.disconnect();
      renderer.dispose();
      sceneRef.current = null;
      cameraRef.current = null;
      rendererRef.current = null;
    };
  }, [canvasContainerRef.current]);

  function addFurniture() {
    if (sceneRef.current) {
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
      const cube = new THREE.Mesh(geometry, material);
      sceneRef.current.add(cube);
      setInterval(() => (cube.rotation.z = cube.rotation.z + 0.01), 20);
    }
  }

  return (
    <div className="project-editor" ref={canvasContainerRef}>
      <button onClick={addFurniture}>add</button>
    </div>
  );
}

function ProjectNameField({ id }: { id: string }) {
  const dispatch = useAppDispatch();
  const project = useAppSelector(selectProjectById(id));
  const disabled = project === undefined;

  function handleNameChange(e: ChangeEvent<HTMLInputElement>) {
    e.preventDefault();
    if (project !== undefined) {
      dispatch(
        optimisticPatchProject({ id: project.id, name: e.target.value }),
      );
    }
  }

  return (
    <input
      type="text"
      value={project?.name || ""}
      placeholder="Untitled Project"
      onChange={handleNameChange}
      disabled={disabled}
    />
  );
}

export function ProjectEditor({ id }: Props) {
  const dispatch = useAppDispatch();
  const project = useAppSelector(selectProjectById(id));

  useEffect(() => {
    if (project === undefined || project.status !== "pending") {
      dispatch(fetchProject(id));
    }
  }, [id]);

  function handleDescriptionChange(e: ChangeEvent<HTMLTextAreaElement>) {
    e.preventDefault();
    if (project !== undefined) {
      dispatch(
        optimisticPatchProject({ id: project.id, description: e.target.value }),
      );
    }
  }

  return (
    <div>
      <div>
        <ProjectNameField id={id} />
      </div>
      <div style={{ border: "1px solid black" }}>
        <Editor id={id} />
      </div>
      <PlanEditor id={id} />
      <FurnitureCatalog />
    </div>
  );
}
