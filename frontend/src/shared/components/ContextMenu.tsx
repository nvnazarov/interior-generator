import "./ContextMenu.scss";
import React, {
  createContext,
  useCallback,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react";

export interface ContextMenuItem {
  icon?: string;
  name?: string;
  divider?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
}

export interface ContextMenuOptions {
  title?: string;
  x?: number;
  y?: number;
  items?: ContextMenuItem[];
}

export interface ContextMenu {
  show: (options: ContextMenuOptions) => void;
  hide: () => void;
}

export const ContextMenuContext = createContext<ContextMenu>({
  show: (_) => {},
  hide: () => {},
});

export function ContextMenuProvider({ children }: { children: ReactNode }) {
  const [options, setOptions] = useState<ContextMenuOptions>({});
  const [isShown, setIsShown] = useState(false);
  const show = useCallback((options: ContextMenuOptions) => {
    setIsShown(true);
    setOptions(options);
  }, []);
  const hide = useCallback(() => {
    setIsShown(false);
  }, []);

  const style: CSSProperties = {
    top: options.y || "20px",
    left: options.x || "20px",
  };

  return (
    <ContextMenuContext.Provider value={{ show, hide }}>
      {children}
      {isShown && (
        <div className="shared__context-menu" style={style}>
          {options.title && <h1>{options.title}</h1>}
          {(options.items || []).map((item, idx) => {
            if (item.divider) {
              return <span key={idx} />;
            } else {
              return (
                <button
                  key={idx}
                  onClick={(e) => {
                    hide();
                    item.onClick?.(e);
                  }}
                >
                  {item.name}
                </button>
              );
            }
          })}
        </div>
      )}
    </ContextMenuContext.Provider>
  );
}
