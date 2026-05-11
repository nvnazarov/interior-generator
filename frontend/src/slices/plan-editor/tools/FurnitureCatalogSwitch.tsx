import { useCallback } from "react";
import { Toggle } from "../../../shared/components/toggle/Toggle";
import { useAppDispatch, useAppSelector } from "../../storeTypes";
import { catalogSwitched, selectIsCatalogOpen } from "../slice";
import { Tooltip } from "../../../shared/components/tooltip/Tooltip";

export function FurnitureCatalogSwitch() {
  const dispatch = useAppDispatch();
  const isOpen = useAppSelector(selectIsCatalogOpen);

  const handleChange = useCallback(() => {
    dispatch(catalogSwitched());
  }, []);

  return (
    <Tooltip content={<p style={{ fontWeight: 400 }}>Furniture catalog</p>}>
      <Toggle icon="furniture.png" onChange={handleChange} checked={isOpen} />
    </Tooltip>
  );
}
