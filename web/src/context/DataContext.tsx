import type {ProgramMeta} from '@/types/data.d.ts';
import type {CollectionEntry} from 'astro:content';
import React, {createContext, useContext, useEffect, useMemo, useState} from 'react';

type DataShape = {
  programs: ProgramMeta[];
  categories: string[];
  tags: string[];
  loading: boolean;
  error: string | null;
};

const DataContext = createContext<DataShape>({
  programs: [],
  categories: [],
  tags: [],
  loading: true,
  error: null,
});

const getCategories = (data: ProgramMeta[]) => {
  return [...new Set(data.map(entry => entry.category))];
};

const getTags = (data: ProgramMeta[]) => {
  return [...new Set(data.map(entry => entry.tags).flat())];
};

export const DataProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [state, setState] = useState<DataShape>({
    programs: [],
    categories: [],
    tags: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch('/api/data.json');
        const data: CollectionEntry<'apps'>[] = await res.json();
        const programsArr = data.map(entry => entry.data);

        const categories = getCategories(programsArr);
        const tags = getTags(programsArr);
        if (!cancelled)
          setState({
            programs: programsArr,
            categories,
            tags,
            loading: false,
            error: null,
          });
      } catch (e: any) {
        if (!cancelled)
          setState(s => ({
            ...s,
            loading: false,
            error: e?.message || 'Failed to load data',
          }));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo(() => state, [state]);
  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

export function useCatalog() {
  return useContext(DataContext);
}
