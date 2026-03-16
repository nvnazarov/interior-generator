import React, { useEffect, useRef, useState, type ChangeEvent } from "react";
import "./FurnitureCatalog.scss";
import { fetchFurniture, selectAllFurniture, type Furniture } from "./slice";
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
      <img src={furniture.thumbnailPath || undefined}></img>
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
  const cursorRef = useRef<string | null>(null);
  const itemsContainerRef = useRef<HTMLDivElement>(null);
  const debouncedName = useDebounce(name, 500);
  useEffect(() => {
    dispatch(
      fetchFurniture({ name, area, limit: 10, cursor: cursorRef.current }),
    ).then((v: any) => {
      cursorRef.current = v.payload.meta.cursor;
    });
  }, [debouncedName, area]);
  useEffect(() => {
    if (itemsContainerRef.current) {
      const loadItemsOnScroll = () => {
        if (itemsContainerRef.current === null) {
          return;
        }
        const { scrollTop, scrollHeight, clientHeight } =
          itemsContainerRef.current;
        if (scrollHeight - scrollTop <= clientHeight + 1) {
          dispatch(
            fetchFurniture({
              name,
              area,
              limit: 10,
              cursor: cursorRef.current,
            }),
          ).then((v: any) => {
            cursorRef.current = v.payload.meta.cursor;
          });
        }
      };
      itemsContainerRef.current.addEventListener("scroll", loadItemsOnScroll);
      loadItemsOnScroll();
      return () => {
        itemsContainerRef.current?.removeEventListener(
          "scroll",
          loadItemsOnScroll,
        );
      };
    }
  }, [itemsContainerRef]);
  function handleNameChange(e: ChangeEvent<HTMLInputElement>) {
    cursorRef.current = null;
    setName(e.target.value);
  }
  function handleAreaChange(e: ChangeEvent<HTMLSelectElement>) {
    cursorRef.current = null;
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
      <div
        className="furniture-catalog__items-container"
        ref={itemsContainerRef}
      >
        {furniture
          .filter((f) => {
            if (!f.name.includes(name)) return false;
            if (area !== "" && f.meta.area !== area) return false;
            return true;
          })
          .map((furniture, idx) => (
            <FurnitureCatalogItem key={idx} furniture={furniture} />
          ))}
      </div>
    </div>
  );
}
