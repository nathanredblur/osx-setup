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

export function singleInstallCommand(p: ProgramMeta): string | null {
  if (!p.bundle) return null;
  return bundleToCommand(p.bundle);
}

export function createBrewfile(programs: ProgramMeta[]): string {
  const lines: string[] = [];
  let hasMas = false;

  programs.forEach(p => {
    if (p.type === 'mas') hasMas = true;
    if (p.bundle) {
      lines.push(p.bundle);
    }
  });

  if (hasMas) {
    lines.unshift('brew "mas"');
  }

  return lines.join('\n') + '\n';
}

export function createPostConfig(programs: ProgramMeta[]): string {
  const lines: string[] = ['#!/bin/bash'];
  lines.push('');
  lines.push('echo "🔧 Starting post-installation configuration..."');
  lines.push('echo "=============================================="');
  lines.push('');

  const configCommands = programs
    .filter(p => p.configure)
    .map(p => p.configure)
    .filter((cmd): cmd is string => Boolean(cmd));

  if (configCommands.length > 0) {
    lines.push(...configCommands);
  } else {
    lines.push('echo "No configuration scripts found."');
  }

  lines.push('');
  lines.push('echo "✅ Post-configuration completed!"');

  return lines.join('\n') + '\n';
}

export function createCustomInstall(programs: ProgramMeta[]): string {
  const lines: string[] = ['#!/bin/bash'];
  lines.push('');
  lines.push('echo "📦 Starting custom installations..."');
  lines.push('echo "===================================="');
  lines.push('');

  const installCommands = programs
    .filter(p => p.install)
    .map(p => p.install)
    .filter((cmd): cmd is string => Boolean(cmd));

  if (installCommands.length > 0) {
    lines.push(...installCommands);
  } else {
    lines.push('echo "No custom installation scripts found."');
  }

  lines.push('');
  lines.push('echo "✅ Custom installations completed!"');

  return lines.join('\n') + '\n';
}
