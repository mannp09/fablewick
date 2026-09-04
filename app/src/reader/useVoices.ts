import { useEffect, useState } from 'react';

// speechSynthesis.getVoices() is often empty on first call and fills in
// asynchronously (voiceschanged) once the browser's TTS engine reports
// in. Playwright's headless Chromium never fires it and stays empty,
// which is the exact case read-aloud has to fail gracefully in.
export function speechSupported(): boolean {
  return typeof window !== 'undefined' && 'speechSynthesis' in window;
}

export function useVoices(): SpeechSynthesisVoice[] {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>(() =>
    speechSupported() ? window.speechSynthesis.getVoices() : [],
  );

  useEffect(() => {
    if (!speechSupported()) return;
    const update = () => setVoices(window.speechSynthesis.getVoices());
    update();
    window.speechSynthesis.addEventListener('voiceschanged', update);
    return () => window.speechSynthesis.removeEventListener('voiceschanged', update);
  }, []);

  return voices;
}

// First installed voice whose lang starts with the page's language code
// (e.g. "hi" matches "hi-IN"). Undefined means this device has no voice
// for that language at all - the read-aloud button disables itself and
// says so, rather than speaking in the wrong language.
export function findVoice(
  voices: SpeechSynthesisVoice[],
  langCode: string,
): SpeechSynthesisVoice | undefined {
  const code = langCode.toLowerCase();
  return voices.find((v) => v.lang.toLowerCase().startsWith(code));
}
