import React, { useMemo, useState } from "react";
import AppCard from "@/components/AppCard";
import { useCatalog } from "@/context/DataContext";
import { useFiltersStore } from "@/stores/filters";
import { createProgramsFuse, fuzzySearch } from "@/lib/fuzzy";
import { useSelectionStore } from "@/stores/selection";
import AppDetail from "@/components/AppDetail";

const AppGrid: React.FC = () => {
  const { programs, loading } = useCatalog();
  const { query, category, view } = useFiltersStore();
  const selectedIds = useSelectionStore((s) => s.selectedIds);
  const [detailId, setDetailId] = useState<string | null>(null);
  const toggle = useSelectionStore((s) => s.toggle);

  const filtered = useMemo(() => {
    let list = programs;
    if (category) list = list.filter((p) => p.category === category);
    if (view === "selected")
      list = list.filter((p) => Boolean(selectedIds[p.id]));
    // tag/paid/settings filters removed; fuzzy search covers tags
    if (query.trim()) {
      const fuse = createProgramsFuse(list);
      list = fuzzySearch(fuse, query);
    }
    return list;
  }, [programs, query, category, view, selectedIds]);

  return (
    <div className="p-4 grid gap-5 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {loading && (
        <div className="col-span-full text-sm text-neutral-500">
          Loading catalog…
        </div>
      )}
      {!loading &&
        filtered.map((p) => (
          <div key={p.id} onClick={() => setDetailId(p.id)}>
            <AppCard program={p} />
          </div>
        ))}
      <AppDetail
        program={filtered.find((p) => p.id === detailId) || null}
        selected={Boolean(
          useSelectionStore.getState().selectedIds[detailId || ""]
        )}
        onToggle={() => {
          const program = filtered.find((p) => p.id === detailId);
          if (program) toggle(program);
        }}
        onClose={() => setDetailId(null)}
      />
    </div>
  );
};

export default AppGrid;
