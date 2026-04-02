import type { NewsItem } from '../types';
import { scoreColor } from '../api';

interface Props {
  item: NewsItem;
  highlightText?: string;
  category?: string;
}

export default function NewsCard({ item, highlightText }: Props) {
  const colorClass = scoreColor(item.importance_score);

  return (
    <a
      href={item.source_url}
      target="_blank"
      rel="noreferrer"
      className="block group bg-surface-container hover:bg-surface-container-high border border-transparent hover:border-outline-variant/20 rounded-xl p-5 transition-all duration-200"
    >
      <div className="flex justify-between items-start gap-3 mb-2">
        <h4
          className="font-headline font-semibold text-base text-on-surface group-hover:text-secondary transition-colors line-clamp-2"
          {...(highlightText
            ? { dangerouslySetInnerHTML: { __html: item.name } }
            : {})}
        >
          {!highlightText && item.name}
        </h4>
        <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-bold ${colorClass}`}>
          {item.importance_score}/10
        </span>
      </div>
      <p
        className="text-on-surface-variant text-sm leading-relaxed mb-3 line-clamp-2"
        {...(highlightText
          ? { dangerouslySetInnerHTML: { __html: item.description } }
          : {})}
      >
        {!highlightText && item.description}
      </p>
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-1.5">
          {item.tags.slice(0, 4).map(tag => (
            <span key={tag} className="text-xs text-tertiary bg-tertiary/10 px-2 py-0.5 rounded-md">
              #{tag}
            </span>
          ))}
        </div>
        <span className="text-xs text-outline-variant shrink-0 ml-3">{item.source_name}</span>
      </div>
    </a>
  );
}
