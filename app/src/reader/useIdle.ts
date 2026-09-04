import { useEffect, useState } from 'react';

// True once `active` has held with no pointer movement for `timeoutMs`.
// Used to auto-hide the top bar in full screen; any movement (or leaving
// full screen, which drops `active` to false) shows it again instantly.
export function useIdle(active: boolean, timeoutMs = 2000): boolean {
  const [idle, setIdle] = useState(false);

  useEffect(() => {
    if (!active) {
      setIdle(false);
      return;
    }
    let timer: ReturnType<typeof window.setTimeout>;
    const reset = () => {
      setIdle(false);
      window.clearTimeout(timer);
      timer = window.setTimeout(() => setIdle(true), timeoutMs);
    };
    reset();
    window.addEventListener('pointermove', reset);
    window.addEventListener('pointerdown', reset);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener('pointermove', reset);
      window.removeEventListener('pointerdown', reset);
    };
  }, [active, timeoutMs]);

  return idle;
}
