import React, { useMemo } from "react";
import { useSelectionStore } from "@/stores/selection";
import { createBrewBundle } from "@/lib/bundle";
import { saveTextFile } from "@/lib/file";
import { useToast } from "@/components/Toast";
import { useCatalog } from "@/context/DataContext";

const SummaryPanel: React.FC = () => {
  const selected = useSelectionStore((s) => s.selectedIds);
  const stats = useMemo(() => {
    const items = Object.values(selected);
    const counts = {
      total: items.length,
      brew: 0,
      cask: 0,
      mas: 0,
      settings: 0,
      paid: 0,
    };
    for (const p of items) {
      if (p.type === "brew") counts.brew++;
      if (p.type === "cask") counts.cask++;
      if (p.type === "mas") counts.mas++;
      if (p.hasSettings) counts.settings++;
      if (p.paid) counts.paid++;
    }
    return counts;
  }, [selected]);

  const toast = useToast();
  const { categories } = useCatalog();

  async function handleCreateSetup() {
    const items = Object.values(selected);
    if (items.length === 0) {
      toast("Nothing selected");
      return;
    }
    const script = createBrewBundle(items);
    await saveTextFile("mac-setup.sh", script);
    toast("Setup script generated");
  }

  const selectedList = Object.values(selected);
  const byCategory = useMemo(() => {
    const map: Record<string, number> = {};
    for (const p of selectedList) {
      const key = p.category || "Uncategorized";
      map[key] = (map[key] || 0) + 1;
    }
    return map;
  }, [selectedList]);

  return (
    <aside className="w-96 shrink-0 border-l border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#0f131a] h-full flex flex-col">
      <div className="p-4 border-b border-neutral-200 dark:border-neutral-800">
        <h2 className="text-sm font-semibold tracking-wide uppercase text-neutral-500">
          Summary
        </h2>
      </div>
      <div className="p-4 space-y-4 text-sm">
        <div>
          <div className="flex items-center justify-between">
            <span>Selected</span>
            <span className="font-medium">{stats.total}</span>
          </div>
          <div className="mt-2 h-2 rounded bg-neutral-800/40">
            <div
              className="h-2 rounded bg-blue-600"
              style={{ width: `${Math.min(100, stats.total)}%` }}
            />
          </div>
        </div>
        <button
          onClick={handleCreateSetup}
          className="w-full py-3 rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold"
        >
          create setup
        </button>

        <div className="pt-2">
          <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">
            By category
          </div>
          <div className="space-y-1">
            {Object.keys(byCategory).length === 0 && (
              <div className="text-neutral-500">No selection</div>
            )}
            {categories.map((c) => (
              <div key={c.id} className="flex justify-between">
                <span>{c.name}</span>
                <span className="font-medium">{byCategory[c.name] || 0}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-2">
          <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">
            Selected apps
          </div>
          <div className="space-y-2 max-h-64 overflow-auto pr-2">
            {selectedList.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between bg-neutral-900/40 rounded px-2 py-1"
              >
                <div className="truncate text-sm" title={p.name}>
                  {p.name}
                </div>
                <button
                  className="text-xs px-2 py-0.5 rounded border border-neutral-700 hover:bg-neutral-800"
                  onClick={() => useSelectionStore.getState().toggle(p)}
                >
                  Remove
                </button>
              </div>
            ))}
            {selectedList.length === 0 && (
              <div className="text-neutral-500">Nothing selected yet</div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default SummaryPanel;
