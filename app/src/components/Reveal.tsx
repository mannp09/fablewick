import { useEffect, useRef, useState, type ReactNode } from 'react';
import './Reveal.css';

interface RevealProps {
  children: ReactNode;
  className?: string;
}

// A light fade-up on scroll: mount observes the element with an
// IntersectionObserver, adds .in once it crosses the viewport, and
// disconnects (fires once, never re-hides). Under prefers-reduced-motion
// the CSS rule below removes the transform/opacity transition entirely,
// so no observer plumbing is needed to honor that preference.
export default function Reveal({ children, className }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15, rootMargin: '-10% 0px' },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={['reveal', visible ? 'in' : '', className].filter(Boolean).join(' ')}>
      {children}
    </div>
  );
}
