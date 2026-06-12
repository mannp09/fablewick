// Cloudflare Pages Function — POST /api/generate
// Runs at the edge. Rate-limited per IP via Cloudflare KV.
// Provider-agnostic: Gemini Flash (primary) → Claude Haiku (fallback).

import { generateStory, type ProviderEnv } from '../../src/lib/ai-provider';
import type { LevelKey } from '../../src/lib/reading-levels';

interface Env extends ProviderEnv {
  FABLEWICK_KV?: KVNamespace;
  PER_IP_DAILY_LIMIT?: string;
  GLOBAL_DAILY_LIMIT?: string;
}

interface KVNamespace {
  get(key: string): Promise<string | null>;
  put(key: string, value: string, opts?: { expirationTtl?: number }): Promise<void>;
}

const DEFAULT_IP_LIMIT = 5;
const DEFAULT_GLOBAL_LIMIT = 500;
const SECONDS_PER_DAY = 24 * 60 * 60;

function todayKey(prefix: string, id: string): string {
  const d = new Date();
  const ymd = `${d.getUTCFullYear()}${String(d.getUTCMonth() + 1).padStart(2, '0')}${String(d.getUTCDate()).padStart(2, '0')}`;
  return `${prefix}:${ymd}:${id}`;
}

async function incrementCounter(kv: KVNamespace, key: string, limit: number): Promise<{ allowed: boolean; count: number }> {
  const cur = parseInt((await kv.get(key)) ?? '0', 10);
  if (cur >= limit) return { allowed: false, count: cur };
  await kv.put(key, String(cur + 1), { expirationTtl: SECONDS_PER_DAY * 2 });
  return { allowed: true, count: cur + 1 };
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const body = await request.json() as {
      topic?: string;
      character?: string;
      theme?: string;
      level?: number;
    };

    if (!body.topic || typeof body.topic !== 'string' || body.topic.length < 3) {
      return json({ error: 'Please describe what the story should be about.' }, 400);
    }
    if (body.topic.length > 500) {
      return json({ error: 'Topic is too long.' }, 400);
    }
    const level = (Number(body.level) || 2) as LevelKey;
    if (![1, 2, 3].includes(level)) {
      return json({ error: 'Invalid reading level.' }, 400);
    }

    // Rate limit (only if KV is bound)
    if (env.FABLEWICK_KV) {
      const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
      const ipLimit = parseInt(env.PER_IP_DAILY_LIMIT || '', 10) || DEFAULT_IP_LIMIT;
      const globalLimit = parseInt(env.GLOBAL_DAILY_LIMIT || '', 10) || DEFAULT_GLOBAL_LIMIT;

      const ipCheck = await incrementCounter(env.FABLEWICK_KV, todayKey('ip', ip), ipLimit);
      if (!ipCheck.allowed) {
        return json({ error: `You've made ${ipLimit} stories today. Come back tomorrow — these things take a little time to write.` }, 429);
      }
      const globalCheck = await incrementCounter(env.FABLEWICK_KV, todayKey('global', 'all'), globalLimit);
      if (!globalCheck.allowed) {
        return json({ error: 'Fablewick has reached today\'s story limit. The wick needs a rest. Come back tomorrow.' }, 429);
      }
    }

    const result = await generateStory(
      {
        topic: body.topic,
        character: body.character || undefined,
        theme: body.theme || undefined,
        level,
      },
      {
        GEMINI_API_KEY: env.GEMINI_API_KEY,
        ANTHROPIC_API_KEY: env.ANTHROPIC_API_KEY,
      },
    );

    return json(result);
  } catch (err: any) {
    console.error('[generate] error:', err);
    return json({ error: err?.message || 'Generation failed.' }, 500);
  }
};

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

// Cloudflare types shim (so this file can typecheck without @cloudflare/workers-types installed)
declare global {
  type PagesFunction<E = unknown> = (ctx: { request: Request; env: E }) => Response | Promise<Response>;
}
