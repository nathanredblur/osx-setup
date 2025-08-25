import type {CollectionEntry} from 'astro:content';

export type ProgramMeta = CollectionEntry<'apps'>['data'];
export type InstallType = ProgramMeta['type'];

export interface Parameter {
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'email';
  required: boolean;
  default?: string;
}

export type ParameterValues = Record<string, string>;
export type AppParameterValues = Record<string, ParameterValues>;
