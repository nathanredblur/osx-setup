import React, { useMemo, useState } from "react";
import AppCard from "../items/AppCard";
import { useCatalog } from "../data/DataContext";
import { useFiltersStore } from "../../stores/filters";
import { createProgramsFuse, fuzzySearch } from "../../lib/fuzzy";
import AppDetail from "../modals/AppDetail";
import { useSelectionStore } from "../../stores/selection";

const AppGrid: React.FC = () => {
  const { programs, loading } = useCatalog();
  const { query, category, tag, onlyPaid, onlyWithSettings } =
    useFiltersStore();
  const [detailId, setDetailId] = useState<string | null>(null);
  const toggle = useSelectionStore((s) => s.toggle);

  const filtered = useMemo(() => {
    let list = programs;
    if (category) list = list.filter((p) => p.category === category);
    if (tag) list = list.filter((p) => (p.tags || []).includes(tag));
    if (onlyPaid) list = list.filter((p) => !!p.paid);
    if (onlyWithSettings) list = list.filter((p) => !!p.hasSettings);
    if (query.trim()) {
      const fuse = createProgramsFuse(list);
      list = fuzzySearch(fuse, query);
    }
    return list;
  }, [programs, query, category, tag, onlyPaid, onlyWithSettings]);

  return (
    <div className="p-4 grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
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
