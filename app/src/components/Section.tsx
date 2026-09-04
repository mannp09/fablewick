import type { ReactNode } from 'react';
import './Section.css';

interface SectionProps {
  id?: string;
  title?: string;
  lede?: string;
  className?: string;
  children: ReactNode;
}

export default function Section({ id, title, lede, className, children }: SectionProps) {
  return (
    <section id={id} className={['section', className].filter(Boolean).join(' ')}>
      <div className="section-inner">
        {title && (
          <h2 className="section-title">
            <span className="section-title-text">{title}</span>
          </h2>
        )}
        {lede && <p className="section-lede">{lede}</p>}
        <div className="section-body">{children}</div>
      </div>
    </section>
  );
}
