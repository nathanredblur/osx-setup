import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface FiltersState {
  query: string;
  category: string | null;
  // removed tag/onlyPaid/onlyWithSettings per new spec
  setQuery: (q: string) => void;
  setCategory: (c: string | null) => void;
  clear: () => void;
}

export const useFiltersStore = create<FiltersState>()(
  persist(
    (set) => ({
      query: "",
      category: null,
      setQuery: (q) => set({ query: q }),
      setCategory: (c) => set({ category: c }),
      clear: () => set({ query: "", category: null }),
    }),
    { name: "store.filters" }
  )
);
