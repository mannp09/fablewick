export type LevelKey = 1 | 2 | 3;

export interface LevelDef {
  key: LevelKey;
  label: string;
  age: string;
  description: string;
  wordTarget: [number, number];
  vocab: string;
  sentence: string;
}

export const LEVELS: Record<LevelKey, LevelDef> = {
  1: {
    key: 1,
    label: 'Little Listener',
    age: 'Ages 3–5',
    description: 'Short, warm stories with rhythm and repetition. Made to be read aloud.',
    wordTarget: [150, 250],
    vocab: 'common words only, concrete and sensory',
    sentence: 'short, 5–8 words, lots of repetition',
  },
  2: {
    key: 2,
    label: 'New Reader',
    age: 'Ages 5–7',
    description: 'Early chapter-style stories with characters that grow and learn.',
    wordTarget: [400, 600],
    vocab: 'grade-appropriate, 1–2 new words gently defined in context',
    sentence: 'mixed length, 8–15 words, compound sentences allowed',
  },
  3: {
    key: 3,
    label: 'On Your Own',
    age: 'Ages 7–10',
    description: 'Richer stories with dialogue, deeper themes, and open questions to think about.',
    wordTarget: [800, 1200],
    vocab: 'rich vocabulary, figurative language welcome',
    sentence: 'complex sentences, dialogue, varied rhythm',
  },
};

export const LEVEL_KEYS: LevelKey[] = [1, 2, 3];

export function getLevel(key: number | string): LevelDef {
  const k = Number(key) as LevelKey;
  return LEVELS[k] ?? LEVELS[2];
}
