import AppCard from '@/components/AppCard';
import AppDetail from '@/components/AppDetail';
import {useCatalog} from '@/context/DataContext';
import {createProgramsFuse, fuzzySearch} from '@/lib/fuzzy';
import {useFiltersStore} from '@/stores/filters';
import {useModalStore} from '@/stores/modal';
import {useSelectionStore} from '@/stores/selection';
import React, {useMemo} from 'react';

const AppGrid: React.FC = () => {
  const {programs, loading} = useCatalog();
  const {query, category, view} = useFiltersStore();
  const selectedIds = useSelectionStore(s => s.selectedIds);
  const {detailAppId, openAppDetail, closeAppDetail} = useModalStore();

  const filtered = useMemo(() => {
    let list = programs;
    if (category) list = list.filter(p => p.category === category);
    if (view === 'selected') list = list.filter(p => Boolean(selectedIds[p.id]));
    // tag/paid/settings filters removed; fuzzy search covers tags
    if (query.trim()) {
      const fuse = createProgramsFuse(list);
      list = fuzzySearch(fuse, query);
    }
    // Sort alphabetically by name
    list = list.sort((a, b) => a.name.localeCompare(b.name));
    return list;
  }, [programs, query, category, view, selectedIds]);

  const programSelected = useMemo(() => {
    return programs.find(p => p.id === detailAppId) || null;
  }, [programs, detailAppId]);

  return (
    <div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-5 p-4">
      {loading && <div className="col-span-full text-sm text-neutral-500">Loading catalog…</div>}
      {!loading &&
        filtered.map(p => <AppCard program={p} key={p.id} onClick={() => openAppDetail(p.id)} />)}

      {programSelected && <AppDetail program={programSelected} onClose={closeAppDetail} />}
    </div>
  );
};

export default AppGrid;
