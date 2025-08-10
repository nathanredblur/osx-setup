import React from "react";
import * as Icons from "lucide-react";
import { useFiltersStore } from "@/stores/filters";
import { useCatalog } from "@/context/DataContext";
import CategoryMenu from "@/components/CategoryMenu";

const FiltersBar: React.FC = () => {
  const { query, category, view, setQuery, setCategory, setView, clear } =
    useFiltersStore();
  const { categories } = useCatalog();

  // Temporary type wrappers for lucide components to satisfy React type mismatch
  const IconSearch = Icons.Search as unknown as React.FC<any>;
  const IconGrid = Icons.Grid2X2 as unknown as React.FC<any>;
  const IconList = Icons.ListChecks as unknown as React.FC<any>;

  return (
    <div className="sticky top-0 z-10 bg-white/70 dark:bg-[#0b0e14]/80 backdrop-blur border-b border-neutral-200 dark:border-neutral-800">
      <div className="p-3 flex items-center gap-3">
        <div className="relative flex-1 max-w-xl">
          <IconSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
          <input
            type="text"
            className="w-full pl-9 pr-3 py-2 rounded-md bg-neutral-100 dark:bg-neutral-800 outline-none placeholder:text-neutral-400"
            placeholder="Search apps"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <CategoryMenu
          categories={categories}
          value={category}
          onChange={setCategory}
        />
        <div className="inline-flex rounded-md overflow-hidden border border-neutral-300 dark:border-neutral-700">
          <button
            className={`px-3 py-2 text-sm flex items-center gap-1 ${
              view === "all"
                ? "bg-neutral-200 dark:bg-neutral-700"
                : "bg-transparent"
            }`}
            onClick={() => setView("all")}
          >
            <IconGrid className="w-4 h-4" /> App Library
          </button>
          <button
            className={`px-3 py-2 text-sm flex items-center gap-1 ${
              view === "selected"
                ? "bg-neutral-200 dark:bg-neutral-700"
                : "bg-transparent"
            }`}
            onClick={() => setView("selected")}
          >
            <IconList className="w-4 h-4" /> My Apps
          </button>
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
