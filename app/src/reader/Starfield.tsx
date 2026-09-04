import { useMemo } from 'react';

// A fixed field of small twinkling stars behind the reader stage, matching
// the dusk theme already shipped on the live library/reader-*.html pages.
// Positions are seeded once per mount (not on every render) with a plain
// LCG so the field looks organic without pulling in a random-with-no-
// reproducibility dependency; prefers-reduced-motion in Reader.css turns
// the twinkle keyframes off entirely.
function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}

export default function Starfield() {
  const stars = useMemo(() => {
    const rand = seededRandom(42);
    const count = 46;
    return Array.from({ length: count }, (_, i) => ({
      id: i,
      left: (rand() * 98).toFixed(1),
      top: (rand() * 90).toFixed(1),
      size: (2.5 + rand() * 5).toFixed(1),
      duration: (2.6 + rand() * 3.2).toFixed(2),
      delay: (rand() * 5).toFixed(2),
    }));
  }, []);

  return (
    <div className="reader-starfield" aria-hidden="true">
      {stars.map((s) => (
        <span
          key={s.id}
          className="reader-star"
          style={{
            left: `${s.left}%`,
            top: `${s.top}%`,
            width: `${s.size}px`,
            height: `${s.size}px`,
            animationDuration: `${s.duration}s`,
            animationDelay: `${s.delay}s`,
          }}
        />
      ))}
    </div>
  );
}
