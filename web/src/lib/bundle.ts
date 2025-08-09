import type { ProgramMeta } from "../react/types.d.ts";

export function createBrewBundle(programs: ProgramMeta[]): string {
  const lines: string[] = [
    "#!/usr/bin/env bash",
    "set -euo pipefail",
    "",
    'echo "Installing apps..."',
  ];
  for (const p of programs) {
    const cmd =
      p.type === "mas"
        ? `mas install ${p.slug}`
        : p.type === "cask"
        ? `brew install --cask ${p.slug}`
        : `brew install ${p.slug}`;
    lines.push(cmd);
  }
  return lines.join("\n") + "\n";
}
