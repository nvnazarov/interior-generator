import { useCallback } from "react";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "../storeTypes";
import { catalogSwitched, selectIsCatalogOpen } from "./slice";

export function FurnitureCatalogSwitch() {
  const dispatch = useAppDispatch();
  const isOpen = useAppSelector(selectIsCatalogOpen);

  const handleClick = useCallback(() => {
    dispatch(catalogSwitched());
  }, []);

  return <Button icon="furniture.png" onClick={handleClick} active={isOpen} />;
}
