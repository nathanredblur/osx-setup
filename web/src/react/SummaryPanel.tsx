import React, { useMemo } from "react";
import { useSelectionStore } from "../stores/selection";
import { createBrewBundle } from "../lib/bundle";
import { saveTextFile } from "../lib/file";
import { useToast } from "./toast/Toast";

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

  return (
    <aside className="w-72 shrink-0 border-r border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950 h-full flex flex-col">
      <div className="p-4 border-b border-neutral-200 dark:border-neutral-800">
        <h2 className="text-sm font-semibold tracking-wide uppercase text-neutral-500">
          Summary
        </h2>
      </div>
      <div className="p-4 space-y-4 text-sm">
        <div className="flex justify-between">
          <span>Selected</span>
          <span className="font-medium">{stats.total}</span>
        </div>
        <div className="flex justify-between">
          <span>brew</span>
          <span className="font-medium">{stats.brew}</span>
        </div>
        <div className="flex justify-between">
          <span>cask</span>
          <span className="font-medium">{stats.cask}</span>
        </div>
        <div className="flex justify-between">
          <span>mas</span>
          <span className="font-medium">{stats.mas}</span>
        </div>
        <div className="flex justify-between">
          <span>with settings</span>
          <span className="font-medium">{stats.settings}</span>
        </div>
        <div className="flex justify-between">
          <span>paid</span>
          <span className="font-medium">{stats.paid}</span>
        </div>
      </div>
      <div className="mt-auto p-4">
        <button
          onClick={handleCreateSetup}
          className="w-full py-3 rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold"
        >
          create setup
        </button>
      </div>
    </aside>
  );
};

export default SummaryPanel;
