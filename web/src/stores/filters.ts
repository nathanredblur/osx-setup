import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface FiltersState {
  query: string;
  category: string | null;
  // removed tag/onlyPaid/onlyWithSettings per new spec
  view: "all" | "selected";
  setQuery: (q: string) => void;
  setCategory: (c: string | null) => void;
  setView: (v: "all" | "selected") => void;
  clear: () => void;
}

export const useFiltersStore = create<FiltersState>()(
  persist(
    (set) => ({
      query: "",
      category: null,
      view: "all",
      setQuery: (q) => set({ query: q }),
      setCategory: (c) => set({ category: c }),
      setView: (v) => set({ view: v }),
      clear: () => set({ query: "", category: null, view: "all" }),
    }),
    { name: "store.filters" }
  )
);
