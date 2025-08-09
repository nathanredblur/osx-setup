import React, { useMemo } from "react";
import { Search } from "lucide-react";
import { useFiltersStore } from "../stores/filters";
import { useCatalog } from "./data/DataContext";

const FiltersBar: React.FC = () => {
  const {
    query,
    category,
    tag,
    onlyPaid,
    onlyWithSettings,
    setQuery,
    setCategory,
    setTag,
    setOnlyPaid,
    setOnlyWithSettings,
    clear,
  } = useFiltersStore();
  const { categories, tags } = useCatalog();

  const sortedTags = useMemo(() => tags.slice().sort(), [tags]);

  return (
    <div className="sticky top-0 z-10 bg-white/70 dark:bg-neutral-900/70 backdrop-blur border-b border-neutral-200 dark:border-neutral-800">
      <div className="p-3 flex items-center gap-3">
        <div className="relative flex-1 max-w-xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
          <input
            type="text"
            className="w-full pl-9 pr-3 py-2 rounded-md bg-neutral-100 dark:bg-neutral-800 outline-none"
            placeholder="Search apps"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <select
          className="px-3 py-2 rounded-md bg-neutral-100 dark:bg-neutral-800"
          value={category ?? ""}
          onChange={(e) => setCategory(e.target.value || null)}
        >
          <option value="">Category</option>
          {categories.map((c) => (
            <option key={c.id} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          className="px-3 py-2 rounded-md bg-neutral-100 dark:bg-neutral-800"
          value={tag ?? ""}
          onChange={(e) => setTag(e.target.value || null)}
        >
          <option value="">Tag</option>
          {sortedTags.slice(0, 200).map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={onlyPaid}
            onChange={(e) => setOnlyPaid(e.target.checked)}
          />{" "}
          Only paid
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={onlyWithSettings}
            onChange={(e) => setOnlyWithSettings(e.target.checked)}
          />{" "}
          Only with settings
        </label>
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
