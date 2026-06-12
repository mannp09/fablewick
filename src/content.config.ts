import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const books = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/books' }),
  schema: z.object({
    title: z.string(),
    author: z.string().default('Fablewick Community'),
    ageRange: z.tuple([z.number(), z.number()]),
    themes: z.array(z.string()),
    lesson: z.string(),
    summary: z.string(),
    coverIllustration: z.string(),
    coverColor: z.string().default('amber'),
    levels: z.object({
      '1': z.object({ label: z.string(), wordCount: z.number(), text: z.string() }),
      '2': z.object({ label: z.string(), wordCount: z.number(), text: z.string() }),
      '3': z.object({ label: z.string(), wordCount: z.number(), text: z.string() }),
    }),
  }),
});

export const collections = { books };
