import { useCallback, useEffect, useRef, useState } from 'react';
import { findVoice, speechSupported, useVoices } from './useVoices';

export type ReadAloudStatus = 'idle' | 'speaking' | 'paused';

interface UseReadAloudArgs {
  text: string;
  lang: string;
}

interface UseReadAloudResult {
  supported: boolean;
  hasVoice: boolean;
  status: ReadAloudStatus;
  toggle: () => void;
  stop: () => void;
}

// One play/pause button per page: idle -> speaking on first press,
// speaking -> paused, paused -> speaking again. Stops outright (and the
// button resets to idle) whenever the page or language changes, since a
// held utterance for the old text makes no sense once it's off-screen.
export function useReadAloud({ text, lang }: UseReadAloudArgs): UseReadAloudResult {
  const voices = useVoices();
  const voice = findVoice(voices, lang);
  const supported = speechSupported();
  const hasVoice = supported && voice !== undefined;
  const [status, setStatus] = useState<ReadAloudStatus>('idle');
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const stop = useCallback(() => {
    if (supported) window.speechSynthesis.cancel();
    utteranceRef.current = null;
    setStatus('idle');
  }, [supported]);

  // Text or language changed under an active reading (page turned,
  // language switched mid-story) - the in-flight utterance is now
  // reading text that isn't showing anymore, so cancel it and drop the
  // button back to idle.
  useEffect(() => {
    return () => {
      if (supported) window.speechSynthesis.cancel();
      setStatus('idle');
    };
  }, [text, lang, supported]);

  const toggle = useCallback(() => {
    if (!supported || !hasVoice) return;

    if (status === 'speaking') {
      window.speechSynthesis.pause();
      setStatus('paused');
      return;
    }
    if (status === 'paused') {
      window.speechSynthesis.resume();
      setStatus('speaking');
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    if (voice) utterance.voice = voice;
    utterance.onend = () => setStatus('idle');
    utterance.onerror = () => setStatus('idle');
    utteranceRef.current = utterance;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setStatus('speaking');
  }, [supported, hasVoice, status, text, voice]);

  return { supported, hasVoice, status, toggle, stop };
}
