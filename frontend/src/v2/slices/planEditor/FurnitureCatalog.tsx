import "./FurnitureCatalog.scss";
import { useCallback, useState, type ChangeEvent, type UIEvent } from "react";
import type { Furniture } from "../api/entities";
import { useGetFurnitureInfiniteQuery } from "../api/slice";
import { useDebounce } from "../../shared/hooks/debounce";

function Item({ furniture }: { furniture: Furniture }) {
  return (
    <div>
      <img src={furniture.thumbnailPath} />
      <p>{furniture.name}</p>
      <p>
        {furniture.width}x{furniture.depth}x{furniture.height}
      </p>
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
    console.log(e.currentTarget.scrollHeight);
    if (true) {
      fetchNextPage();
    }
  }, []);

  return (
    <div className="editor__furniture-catalog">
      <div>
        <input value={name} onChange={handleNameChange} />
        <select value={area || undefined} onChange={handleAreaChange}>
          <option value="">Any</option>
          <option value="kitchen">Kitchen</option>
          <option value="bedroom">Bedroom</option>
        </select>
      </div>
      <div
        className="editor__furniture-catalog__feed"
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
