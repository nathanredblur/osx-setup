import type { ProgramMeta } from "../react/types.d.ts";

export function createBrewBundle(programs: ProgramMeta[]): string {
  const lines: string[] = [
    "#!/usr/bin/env bash",
    "set -euo pipefail",
    "",
    'echo "Installing apps..."',
  ];
  for (const p of programs) {
    if (p.type === "mas" && p.masId) {
      lines.push(`mas install ${p.masId}`);
      continue;
    }
    if (p.type === "cask") {
      const token = p.token || p.slug || p.id;
      lines.push(`brew install --cask ${token}`);
      continue;
    }
    if (p.type === "brew") {
      const token = p.token || p.slug || p.id;
      lines.push(`brew install ${token}`);
      continue;
    }
  }
  return lines.join("\n") + "\n";
}

export function singleInstallCommand(p: ProgramMeta): string | null {
  if (p.type === "mas" && p.masId) return `mas install ${p.masId}`;
  if (p.type === "cask")
    return `brew install --cask ${p.token || p.slug || p.id}`;
  if (p.type === "brew") return `brew install ${p.token || p.slug || p.id}`;
  return null;
}
