import { useCallback, useEffect, useState, type RefObject } from 'react';

interface UseFullscreenResult {
  isFullscreen: boolean;
  toggle: () => void;
  exit: () => void;
}

export function useFullscreen(ref: RefObject<HTMLElement | null>): UseFullscreenResult {
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const onChange = () => setIsFullscreen(document.fullscreenElement === ref.current);
    document.addEventListener('fullscreenchange', onChange);
    return () => document.removeEventListener('fullscreenchange', onChange);
  }, [ref]);

  const toggle = useCallback(() => {
    if (document.fullscreenElement) {
      void document.exitFullscreen();
    } else {
      void ref.current?.requestFullscreen();
    }
  }, [ref]);

  const exit = useCallback(() => {
    if (document.fullscreenElement) void document.exitFullscreen();
  }, []);

  return { isFullscreen, toggle, exit };
}
