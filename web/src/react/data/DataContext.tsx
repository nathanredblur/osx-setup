import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ProgramMeta } from "../types.d.ts";

type DataShape = {
  programs: ProgramMeta[];
  categories: { id: string; name: string }[];
  tags: string[];
  loading: boolean;
  error: string | null;
};

const DataContext = createContext<DataShape>({
  programs: [],
  categories: [],
  tags: [],
  loading: true,
  error: null,
});

function mapType(input?: string): "brew" | "cask" | "mas" | undefined {
  if (!input) return undefined;
  if (input === "brew") return "brew";
  if (input === "mas") return "mas";
  if (input === "brew_cask" || input === "direct_download_dmg") return "cask";
  return undefined;
}

function toProgramMeta(entry: any): ProgramMeta {
  const type = mapType(entry.type);
  const hasSettings = Boolean(
    entry.install_script ||
      entry.configure_script ||
      entry.uninstall_script ||
      (entry.dependencies && entry.dependencies.length > 0)
  );
  const paid = Boolean(entry.requires_license);
  return {
    id: entry.id,
    name: entry.name,
    slug: entry.id,
    icon: entry.image || undefined,
    version: undefined,
    url: entry.url || undefined,
    paid,
    hasSettings,
    type,
    tags: entry.tags || [],
    category: entry.category,
  };
}

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, setState] = useState<DataShape>({
    programs: [],
    categories: [],
    tags: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/data.json");
        const json = await res.json();
        const programsObj = json.programs?.programs || json.programs || {};
        const programsArr = Object.values(programsObj).map(toProgramMeta);
        const categories = (json.categories?.categories || []).map(
          (c: any) => ({ id: c.id, name: c.name })
        );
        const tags = (json.tags?.tags || []).map((t: any) => t.name);
        if (!cancelled)
          setState({
            programs: programsArr,
            categories,
            tags,
            loading: false,
            error: null,
          });
      } catch (e: any) {
        if (!cancelled)
          setState((s) => ({
            ...s,
            loading: false,
            error: e?.message || "Failed to load data",
          }));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo(() => state, [state]);
  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

export function useCatalog() {
  return useContext(DataContext);
}
