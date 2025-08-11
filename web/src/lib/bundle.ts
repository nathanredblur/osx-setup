import type {ProgramMeta} from '@/types/data.d.ts';

const regex = /^(\w+)\s+"([^"]+)"(?:,\s+id:\s+(\d+))?/;

export const bundleToCommand = (bundle: string) => {
  const match = bundle.match(regex);
  if (!match) return null;
  const [, type, name, id] = match;

  if (type === 'mas') return `mas install ${id}`;
  if (type === 'cask') return `brew install --cask ${name}`;
  if (type === 'brew') return `brew install ${name}`;
  return null;
};

export function createBrewBundle(programs: ProgramMeta[]): string {
  const lines: string[] = [
    '#!/usr/bin/env bash',
    'set -euo pipefail',
    '',
    'echo "Installing apps..."',
  ];

  const brewFile: string[] = [];
  const install: string[] = [];
  const configure: string[] = [];
  let hasMas = false;

  programs.forEach(p => {
    if (p.type === 'mas') hasMas = true;
    if (p.bundle) brewFile.push(p.bundle);
    if (p.install) install.push(p.install);
    if (p.configure) configure.push(p.configure);
  });

  if (hasMas) lines.push('brew install mas');

  // if (brewFile) lines.push('brew bundle');
  brewFile.forEach(bundle => {
    const command = bundleToCommand(bundle);
    if (command) lines.push(command);
  });

  if (install.length > 0) lines.push(install.join('\n'));
  if (configure.length > 0) lines.push(configure.join('\n'));

  return lines.join('\n') + '\n';
}

export function singleInstallCommand(p: ProgramMeta): string | null {
  if (!p.bundle) return null;
  return bundleToCommand(p.bundle);
}
