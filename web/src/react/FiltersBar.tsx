import React from "react";
import { Search, AppWindow } from "lucide-react";
import { useFiltersStore } from "../stores/filters";
import { useCatalog } from "./data/DataContext";

const FiltersBar: React.FC = () => {
  const { query, category, setQuery, setCategory, clear } = useFiltersStore();
  const { categories } = useCatalog();

  return (
    <div className="sticky top-0 z-10 bg-white/70 dark:bg-[#0b0e14]/80 backdrop-blur border-b border-neutral-200 dark:border-neutral-800">
      <div className="p-3 flex items-center gap-3">
        <div className="relative flex-1 max-w-xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
          <input
            type="text"
            className="w-full pl-9 pr-3 py-2 rounded-md bg-neutral-100 dark:bg-neutral-800 outline-none placeholder:text-neutral-400"
            placeholder="Search apps"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="relative">
          <select
            className="pl-8 pr-3 py-2 rounded-md bg-neutral-100 dark:bg-neutral-800 appearance-none"
            value={category ?? ""}
            onChange={(e) => setCategory(e.target.value || null)}
            title="All Apps"
          >
            <option value="">All Apps</option>
            {categories.map((c) => (
              <option key={c.id} value={c.name}>
                {c.name}
              </option>
            ))}
          </select>
          <AppWindow className="w-4 h-4 absolute left-2 top-1/2 -translate-y-1/2 text-neutral-500" />
        </div>
        <button
          className="px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700"
          onClick={clear}
        >
          Clear filters
        </button>
      </div>
    </div>
  );
};

export default FiltersBar;
