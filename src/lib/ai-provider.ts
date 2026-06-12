// Provider-agnostic AI generation interface.
// Primary: Google Gemini 2.5 Flash (free tier — 1,500 req/day)
// Fallback: Anthropic Claude Haiku
// Swap providers by changing the env vars in Cloudflare Workers.

import type { LevelKey } from './reading-levels';
import { buildStorySystemPrompt, buildStoryUserPrompt } from './prompts';

export interface GenerateOptions {
  topic: string;
  character?: string;
  theme?: string;
  setting?: string;
  level: LevelKey;
}

export interface GenerateResult {
  markdown: string;
  provider: 'gemini' | 'claude';
}

export interface ProviderEnv {
  GEMINI_API_KEY?: string;
  ANTHROPIC_API_KEY?: string;
}

const GEMINI_MODEL = 'gemini-2.5-flash';
const CLAUDE_MODEL = 'claude-haiku-4-5-20251001';

export async function generateStory(
  opts: GenerateOptions,
  env: ProviderEnv,
): Promise<GenerateResult> {
  const system = buildStorySystemPrompt(opts.level);
  const user = buildStoryUserPrompt(opts);

  // Try Gemini first (free tier)
  if (env.GEMINI_API_KEY) {
    try {
      const markdown = await callGemini(system, user, env.GEMINI_API_KEY);
      return { markdown, provider: 'gemini' };
    } catch (err) {
      console.warn('[ai-provider] Gemini failed, falling back to Claude:', err);
    }
  }

  // Fallback to Claude
  if (env.ANTHROPIC_API_KEY) {
    const markdown = await callClaude(system, user, env.ANTHROPIC_API_KEY);
    return { markdown, provider: 'claude' };
  }

  throw new Error('No AI provider configured. Set GEMINI_API_KEY or ANTHROPIC_API_KEY.');
}

async function callGemini(system: string, user: string, apiKey: string): Promise<string> {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${apiKey}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      systemInstruction: { parts: [{ text: system }] },
      contents: [{ role: 'user', parts: [{ text: user }] }],
      generationConfig: { temperature: 0.85, maxOutputTokens: 2048 },
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Gemini API error ${res.status}: ${errText}`);
  }

  const data = await res.json() as any;
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('Gemini returned empty content');
  return text.trim();
}

async function callClaude(system: string, user: string, apiKey: string): Promise<string> {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: CLAUDE_MODEL,
      max_tokens: 2048,
      system,
      messages: [{ role: 'user', content: user }],
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Claude API error ${res.status}: ${errText}`);
  }

  const data = await res.json() as any;
  const text = data?.content?.[0]?.text;
  if (!text) throw new Error('Claude returned empty content');
  return text.trim();
}
