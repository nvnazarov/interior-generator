import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { catalogSwitched, selectIsCatalogOpen } from "./slice";

export function FurnitureCatalogSwitch() {
  const dispatch = useAppDispatch();
  const isCatalogOpen = useAppSelector(selectIsCatalogOpen);

  const handleClick = useCallback(() => {
    dispatch(catalogSwitched(!isCatalogOpen));
  }, [isCatalogOpen]);

  return (
    <Button icon="furniture.png" onClick={handleClick} active={isCatalogOpen} />
  );
}
