import type {CollectionEntry} from 'astro:content';

export type ProgramMeta = CollectionEntry<'apps'>['data'];
export type InstallType = ProgramMeta['type'];
