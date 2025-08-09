import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ProgramMeta } from "../react/types.d.ts";

interface SelectionState {
  selectedIds: Record<string, ProgramMeta>;
  toggle: (program: ProgramMeta) => void;
  clear: () => void;
}

export const useSelectionStore = create<SelectionState>()(
  persist(
    (set, get) => ({
      selectedIds: {},
      toggle: (program) => {
        const current = { ...get().selectedIds };
        if (current[program.id]) {
          delete current[program.id];
        } else {
          current[program.id] = program;
        }
        set({ selectedIds: current });
      },
      clear: () => set({ selectedIds: {} }),
    }),
    { name: "store.selection" }
  )
);
