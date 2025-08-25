import type {ProgramMeta, ParameterValues} from '@/types/data.d.ts';
import {useParametersStore} from '@/stores/parameters';

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

// Function to replace parameters in a script
function replaceParameters(script: string, parameters: ParameterValues): string {
  let result = script;
  
  // Replace {{ parameter.name }} with actual values
  for (const [paramName, paramValue] of Object.entries(parameters)) {
    const placeholder = `{{ ${paramName} }}`;
    const escapedValue = paramValue.replace(/"/g, '\\"'); // Escape quotes for shell safety
    result = result.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), escapedValue);
  }
  
  return result;
}

export function createPostConfig(programs: ProgramMeta[]): string {
  const lines: string[] = ['#!/bin/bash'];
  lines.push('');
  lines.push('echo "🔧 Starting post-installation configuration..."');
  lines.push('echo "=============================================="');
  lines.push('');

  // Get parameters from store
  const parametersStore = useParametersStore.getState();

  const configCommands = programs
    .filter(p => p.configure)
    .map(p => {
      if (!p.configure) return null;
      
      // Get parameters for this program
      const programParameters = parametersStore.getParameters(p.id);
      
      // Replace parameters in the configure script
      return replaceParameters(p.configure, programParameters);
    })
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
