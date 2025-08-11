import {glob} from 'astro/loaders';
import {defineCollection, z} from 'astro:content';

const apps = defineCollection({
  loader: glob({
    pattern: '**/*.yml',
    base: './src/data/apps',
  }),
  schema: z
    .object({
      id: z.string(),
      name: z.string(),
      description: z.string(),
      type: z.enum(['brew', 'cask', 'mas', 'shell_script']),
      category: z.string(),
      selected_by_default: z.boolean().optional().default(false),
      requires_license: z.boolean().optional().default(false),
      tags: z.array(z.string()).optional().default([]),
      image: z.string().nullable().optional().default(null),
      url: z.string().nullable().optional().default(null),
      bundle: z.string().nullable().optional().default(null),
      install: z.string().nullable().optional().default(null),
      notes: z.string().nullable().optional().default(null),
      validate: z.string().nullable().optional().default(null),
      configure: z.string().nullable().optional().default(null),
      uninstall: z.string().nullable().optional().default(null),
    })
    .refine(
      data => {
        if (['brew', 'cask', 'mas'].includes(data.type)) {
          return data.bundle !== null;
        }
        return true;
      },
      {
        message: 'Bundle is required for MAS, Brew, and Cask apps',
      }
    ),
});

export const collections = {apps};
