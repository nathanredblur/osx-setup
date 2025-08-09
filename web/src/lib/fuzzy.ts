import Fuse from "fuse.js";
import type { ProgramMeta } from "../react/types.d.ts";

export function createProgramsFuse(items: ProgramMeta[]): Fuse<ProgramMeta> {
  return new Fuse(items, {
    keys: ["name", "slug", "tags", "category"],
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
