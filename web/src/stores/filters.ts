import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface FiltersState {
  query: string;
  category: string | null;
  tag: string | null;
  onlyPaid: boolean;
  onlyWithSettings: boolean;
  setQuery: (q: string) => void;
  setCategory: (c: string | null) => void;
  setTag: (t: string | null) => void;
  setOnlyPaid: (v: boolean) => void;
  setOnlyWithSettings: (v: boolean) => void;
  clear: () => void;
}

export const useFiltersStore = create<FiltersState>()(
  persist(
    (set) => ({
      query: "",
      category: null,
      tag: null,
      onlyPaid: false,
      onlyWithSettings: false,
      setQuery: (q) => set({ query: q }),
      setCategory: (c) => set({ category: c }),
      setTag: (t) => set({ tag: t }),
      setOnlyPaid: (v) => set({ onlyPaid: v }),
      setOnlyWithSettings: (v) => set({ onlyWithSettings: v }),
      clear: () =>
        set({
          query: "",
          category: null,
          tag: null,
          onlyPaid: false,
          onlyWithSettings: false,
        }),
    }),
    { name: "store.filters" }
  )
);
