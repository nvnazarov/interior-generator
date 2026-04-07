import "./FurnitureCatalog.scss";
import {
  useCallback,
  useState,
  type ChangeEvent,
  type MouseEvent,
  type UIEvent,
} from "react";
import type { Furniture } from "../api/entities";
import { useGetFurnitureInfiniteQuery } from "../api/slice";
import { useDebounce } from "../../shared/hooks/debounce";
import { useAppDispatch } from "../storeTypes";
import {
  finishedDraggingFurniture,
  hideFurniturePreview,
  showFurniturePreview,
  startedDraggingFurniture,
} from "./slice";

function Item({ furniture }: { furniture: Furniture }) {
  const dispatch = useAppDispatch();

  const handleDragStart = useCallback((e: MouseEvent<HTMLDivElement>) => {
    e.stopPropagation();

    document.body.style.userSelect = "none";
    document.body.style.pointerEvents = "auto";

    dispatch(startedDraggingFurniture({ furnitureId: furniture.id }));
    dispatch(
      showFurniturePreview({
        furnitureId: furniture.id,
        x: 0,
        y: 0,
        z: 0,
        yaw: 0,
      }),
    );
  }, []);

  const handleDragEnd = useCallback((e: MouseEvent<HTMLDivElement>) => {
    document.body.style.userSelect = "";
    dispatch(finishedDraggingFurniture());
    dispatch(hideFurniturePreview());
  }, []);

  return (
    <div
      className="plan-editor__furniture-catalog__feed__item"
      onMouseDown={handleDragStart}
      onMouseUp={handleDragEnd}
    >
      <img src={furniture.thumbnailPath || undefined} />
      <p>{furniture.name}</p>
      <span>
        {furniture.width}x{furniture.depth}x{furniture.height} cm<sup>3</sup>
      </span>
    </div>
  );
}

export function FurnitureCatalog() {
  const [name, setName] = useState<string>("");
  const [area, setArea] = useState<string>("");
  const debounced = useDebounce({ name, area }, 500);
  const { data, fetchNextPage } = useGetFurnitureInfiniteQuery({
    name: debounced.name || undefined,
    area: debounced.area || undefined,
    cursor: undefined,
  });

  const handleNameChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  }, []);

  const handleAreaChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
    setArea(e.target.value);
  }, []);

  const handleFeedScroll = useCallback((e: UIEvent<HTMLDivElement>) => {
    if (true) {
      fetchNextPage();
    }
  }, []);

  return (
    <div className="plan-editor__furniture-catalog">
      <div className="plan-editor__furniture-catalog__filters">
        <div>
          <p>Name</p>
          <input value={name} onChange={handleNameChange} />
        </div>
        <div>
          <p>Area</p>
          <select value={area || undefined} onChange={handleAreaChange}>
            <option value="">Any</option>
            <option value="kitchen">Kitchen</option>
            <option value="bedroom">Bedroom</option>
          </select>
        </div>
      </div>
      <div
        className="plan-editor__furniture-catalog__feed"
        onScroll={handleFeedScroll}
      >
        {data?.pages
          .map((page) => page.furniture)
          .flat()
          .map((furniture, idx) => (
            <Item key={idx} furniture={furniture} />
          ))}
      </div>
    </div>
  );
}
