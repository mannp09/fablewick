import { useRef, type PointerEvent } from 'react';

interface SwipeHandlers {
  onPointerDown: (e: PointerEvent) => void;
  onPointerUp: (e: PointerEvent) => void;
}

// Touch-only horizontal swipe (mouse drags are left alone, since a mouse
// on this stage is more likely selecting text or hitting a button than
// paging). A swipe fires only once the horizontal move clears the
// threshold and out-runs any vertical move, so a scroll gesture on a
// tall text column never gets mistaken for a page turn.
export function useSwipe(
  onSwipeLeft: () => void,
  onSwipeRight: () => void,
  threshold = 40,
): SwipeHandlers {
  const start = useRef<{ x: number; y: number } | null>(null);

  const onPointerDown = (e: PointerEvent) => {
    if (e.pointerType !== 'touch') return;
    start.current = { x: e.clientX, y: e.clientY };
  };

  const onPointerUp = (e: PointerEvent) => {
    const from = start.current;
    start.current = null;
    if (!from || e.pointerType !== 'touch') return;
    const dx = e.clientX - from.x;
    const dy = e.clientY - from.y;
    if (Math.abs(dx) < threshold || Math.abs(dx) <= Math.abs(dy)) return;
    if (dx < 0) onSwipeLeft();
    else onSwipeRight();
  };

  return { onPointerDown, onPointerUp };
}
