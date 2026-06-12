import { useState } from 'react';
import { LEVELS, LEVEL_KEYS, type LevelKey } from '../lib/reading-levels';

type Step = 'topic' | 'level' | 'generating' | 'done' | 'error';

export default function StoryGenerator() {
  const [step, setStep] = useState<Step>('topic');
  const [topic, setTopic] = useState('');
  const [character, setCharacter] = useState('');
  const [theme, setTheme] = useState('');
  const [level, setLevel] = useState<LevelKey>(2);
  const [story, setStory] = useState('');
  const [error, setError] = useState('');

  function onSubmitTopic(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim()) return;
    setStep('level');
  }

  async function onPickLevel(k: LevelKey) {
    setLevel(k);
    setStep('generating');
    setError('');
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, character, theme, level: k }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || `Request failed (${res.status})`);
      }
      const data = await res.json();
      setStory(data.markdown);
      setStep('done');
    } catch (err: any) {
      setError(err?.message || 'Something went wrong.');
      setStep('error');
    }
  }

  function reset() {
    setStep('topic');
    setStory('');
    setError('');
  }

  return (
    <div className="max-w-2xl mx-auto">
      {step === 'topic' && (
        <form onSubmit={onSubmitTopic} className="space-y-5">
          <div>
            <label className="block text-sm mb-2" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-ink-soft)' }}>
              What should the story be about?
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="a friendly dragon who is afraid of the dark..."
              className="w-full px-4 py-3 rounded-[var(--radius-soft)] border-2 border-[var(--color-cream-soft)] focus:border-[var(--color-amber)] outline-none transition"
              style={{ fontFamily: 'var(--font-body)', fontSize: '1.05rem', background: 'var(--color-paper)' }}
              autoFocus
              maxLength={300}
              required
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-2" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-ink-soft)' }}>
                Main character's name (optional)
              </label>
              <input
                type="text"
                value={character}
                onChange={(e) => setCharacter(e.target.value)}
                placeholder="e.g. Maya"
                className="w-full px-4 py-3 rounded-[var(--radius-soft)] border-2 border-[var(--color-cream-soft)] focus:border-[var(--color-amber)] outline-none transition"
                style={{ fontFamily: 'var(--font-body)', background: 'var(--color-paper)' }}
                maxLength={50}
              />
            </div>
            <div>
              <label className="block text-sm mb-2" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-ink-soft)' }}>
                A lesson to tuck inside (optional)
              </label>
              <input
                type="text"
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                placeholder="e.g. patience, kindness, sharing"
                className="w-full px-4 py-3 rounded-[var(--radius-soft)] border-2 border-[var(--color-cream-soft)] focus:border-[var(--color-amber)] outline-none transition"
                style={{ fontFamily: 'var(--font-body)', background: 'var(--color-paper)' }}
                maxLength={100}
              />
            </div>
          </div>
          <button type="submit" className="btn-warm" disabled={!topic.trim()}>
            Next: pick a reading level →
          </button>
        </form>
      )}

      {step === 'level' && (
        <div>
          <p className="text-sm mb-5" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-ink-soft)' }}>
            How is your reader doing with books? Pick what feels right — you can re-generate at a different level any time.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {LEVEL_KEYS.map((k) => {
              const lvl = LEVELS[k];
              return (
                <button
                  key={k}
                  type="button"
                  onClick={() => onPickLevel(k)}
                  className="card-cozy text-left p-5"
                  style={{ cursor: 'pointer' }}
                >
                  <div className="text-xs mb-1" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-amber-deep)' }}>{lvl.age}</div>
                  <h3 className="text-lg mb-2" style={{ fontFamily: 'var(--font-display)', fontWeight: 600 }}>{lvl.label}</h3>
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--color-ink-soft)' }}>{lvl.description}</p>
                </button>
              );
            })}
          </div>
          <button onClick={() => setStep('topic')} className="mt-6 text-sm hover:underline" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-ink-soft)' }}>
            ← Change the topic
          </button>
        </div>
      )}

      {step === 'generating' && (
        <div className="text-center py-12">
          <div className="inline-block w-12 h-12 mb-6">
            <svg viewBox="0 0 32 32" className="w-full h-full animate-pulse">
              <circle cx="16" cy="20" r="9" fill="var(--color-amber)" opacity="0.3" />
              <path d="M16 6 C 14 11, 14 14, 16 18 C 18 14, 18 11, 16 6 Z" fill="var(--color-amber-deep)" />
              <circle cx="16" cy="20" r="2" fill="var(--color-rust)" />
            </svg>
          </div>
          <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem' }}>Lighting the wick...</p>
          <p className="text-sm mt-2" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-ink-soft)' }}>This takes about 10–20 seconds.</p>
        </div>
      )}

      {step === 'done' && (
        <div>
          <div className="prose-story whitespace-pre-line p-8 rounded-[var(--radius-warm)]" style={{ background: 'var(--color-paper)' }}>
            {story}
          </div>
          <div className="mt-6 flex gap-3">
            <button onClick={reset} className="btn-warm">Make another</button>
            <button onClick={() => window.print()} className="btn-quiet">Print this story</button>
          </div>
          <p className="text-xs mt-6" style={{ fontFamily: 'var(--font-ui)', color: 'var(--color-ink-soft)' }}>
            ✨ This story was written by AI. An adult should give it a read before sharing with a child.
          </p>
        </div>
      )}

      {step === 'error' && (
        <div className="p-6 rounded-[var(--radius-warm)]" style={{ background: 'var(--color-cream-soft)' }}>
          <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem' }}>The wick wouldn't catch.</p>
          <p className="text-sm mt-2" style={{ color: 'var(--color-ink-soft)' }}>{error}</p>
          <button onClick={reset} className="btn-warm mt-4">Try again</button>
        </div>
      )}
    </div>
  );
}
