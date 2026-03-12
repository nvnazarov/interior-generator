import type React from "react";

export function PlanEditor({ id }: { id: string }) {
  function handleDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
  }
  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    console.log(e.dataTransfer.getData("application/json"));
  }
  return (
    <div onDragOver={handleDragOver} onDrop={handleDrop}>
      Plan Editor: {id}
    </div>
  );
}
