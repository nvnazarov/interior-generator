import React, { useEffect, useState, type ChangeEvent } from "react";
import "./FurnitureCatalog.scss";
import {
  fetchFurniture,
  selectAllFurniture,
  type Furniture,
} from "./furnitureSlice";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { useDebounce } from "../../shared/hooks/debounce";

export function FurnitureCatalogItem({ furniture }: { furniture: Furniture }) {
  function handleDragStart(e: React.DragEvent<HTMLDivElement>) {
    e.dataTransfer.setData("application/json", JSON.stringify(furniture));
  }

  return (
    <div
      className="furniture-catalog__item"
      onDragStart={handleDragStart}
      draggable={true}
    >
      <img src={furniture.thumbnail_path || undefined}></img>
      <div>{furniture.name}</div>
      <div>
        {furniture.width}x{furniture.height}x{furniture.depth}
      </div>
    </div>
  );
}

export function FurnitureCatalog() {
  const dispatch = useAppDispatch();
  const furniture = useAppSelector(selectAllFurniture);
  const [name, setName] = useState("");
  const [area, setArea] = useState("");
  const debouncedName = useDebounce(name, 500);
  useEffect(() => {
    dispatch(fetchFurniture({ name, area }));
  }, [debouncedName, area]);
  function handleNameChange(e: ChangeEvent<HTMLInputElement>) {
    setName(e.target.value);
  }
  function handleAreaChange(e: ChangeEvent<HTMLSelectElement>) {
    setArea(e.target.value);
  }
  return (
    <div className="furniture-catalog">
      <div>Furniture Catalog</div>
      <div className="furniture-catalog__filters-container">
        <input
          type="text"
          value={name}
          placeholder="Search by name"
          onChange={handleNameChange}
        />
        <select value={area} onChange={handleAreaChange}>
          <option value="">Any</option>
          <option value="kitchen">Kitchen</option>
          <option value="bathroom">Bathroom</option>
          <option value="living room">Living room</option>
          <option value="bedroom">Bedroom</option>
          <option value="hall">Hall</option>
        </select>
      </div>
      <div className="furniture-catalog__items-container">
        {furniture.map((furniture, idx) => (
          <FurnitureCatalogItem key={idx} furniture={furniture} />
        ))}
      </div>
    </div>
  );
}
