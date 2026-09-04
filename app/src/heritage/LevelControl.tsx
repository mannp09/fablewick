import { heritageLevelLabel } from './i18n';

interface LevelControlProps {
  levelNames: string[];
  level: string;
  lang: string;
  onChange: (level: string) => void;
  className?: string;
}

// A three-way segmented control (Kids / Adults / Seniors), always all
// visible at once rather than a dropdown - unlike the five-language
// picker, three reading levels is a short enough list to show outright,
// and it's the ruling's own words ("a segmented control").
export default function LevelControl({ levelNames, level, lang, onChange, className }: LevelControlProps) {
  return (
    <div className={['heritage-level-control', className].filter(Boolean).join(' ')} role="group" aria-label="Reading level">
      {levelNames.map((l) => (
        <button
          key={l}
          type="button"
          className={`heritage-level-btn${l === level ? ' active' : ''}`}
          aria-pressed={l === level}
          onClick={() => onChange(l)}
        >
          {heritageLevelLabel(lang, l)}
        </button>
      ))}
    </div>
  );
}
