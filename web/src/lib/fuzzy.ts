import Fuse from "fuse.js";
import type { ProgramMeta } from "@/types/data.d.ts";

export function createProgramsFuse(items: ProgramMeta[]): Fuse<ProgramMeta> {
  return new Fuse(items, {
    keys: [
      { name: "name", weight: 0.6 },
      { name: "slug", weight: 0.3 },
      { name: "tags", weight: 0.3 },
      { name: "category", weight: 0.2 },
    ],
    threshold: 0.35,
    ignoreLocation: true,
  });
}

export function fuzzySearch(
  fuse: Fuse<ProgramMeta>,
  query: string
): ProgramMeta[] {
  if (!query.trim()) return fuse.getIndex().docs as ProgramMeta[];
  return fuse.search(query).map((r) => r.item);
}
