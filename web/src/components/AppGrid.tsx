import AppCard from '@/components/AppCard';
import AppDetail from '@/components/AppDetail';
import {useCatalog} from '@/context/DataContext';
import {createProgramsFuse, fuzzySearch} from '@/lib/fuzzy';
import {useFiltersStore} from '@/stores/filters';
import {useSelectionStore} from '@/stores/selection';
import React, {useMemo, useState} from 'react';

const AppGrid: React.FC = () => {
  const {programs, loading} = useCatalog();
  const {query, category, view} = useFiltersStore();
  const selectedIds = useSelectionStore(s => s.selectedIds);
  const [detailId, setDetailId] = useState<string | null>(null);
  const toggle = useSelectionStore(s => s.toggle);

  const filtered = useMemo(() => {
    let list = programs;
    if (category) list = list.filter(p => p.category === category);
    if (view === 'selected') list = list.filter(p => Boolean(selectedIds[p.id]));
    // tag/paid/settings filters removed; fuzzy search covers tags
    if (query.trim()) {
      const fuse = createProgramsFuse(list);
      list = fuzzySearch(fuse, query);
    }
    return list;
  }, [programs, query, category, view, selectedIds]);

  return (
    <div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-5 p-4">
      {loading && <div className="col-span-full text-sm text-neutral-500">Loading catalog…</div>}
      {!loading &&
        filtered.map(p => <AppCard program={p} key={p.id} onClick={() => setDetailId(p.id)} />)}
      <AppDetail
        program={filtered.find(p => p.id === detailId) || null}
        selected={Boolean(useSelectionStore.getState().selectedIds[detailId || ''])}
        onToggle={() => {
          const program = filtered.find(p => p.id === detailId);
          if (program) toggle(program);
        }}
        onClose={() => setDetailId(null)}
      />
    </div>
  );
};

export default AppGrid;
