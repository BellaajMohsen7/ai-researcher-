import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api, CAT_LABELS, CAT_COLORS } from '../api';
import type { NewsItem } from '../types';
import NewsCard from '../components/NewsCard';

const TIME_OPTIONS = [
  { label: 'Today', days: 1 },
  { label: 'Last 3 Days', days: 3 },
  { label: 'Last 7 Days', days: 7 },
];

const SORT_OPTIONS = ['importance', 'date', 'source'] as const;
type SortOption = typeof SORT_OPTIONS[number];

export default function CategoryView() {
  const { cat = 'ai_models' } = useParams();
  const [items, setItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(1);
  const [sort, setSort] = useState<SortOption>('importance');
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    setLoading(true);
    api.getCategory(cat, days).then(res => {
      setItems(res?.items ?? []);
      setLoading(false);
    });
  }, [cat, days]);

  const sorted = [...items].sort((a, b) => {
    if (sort === 'importance') return b.importance_score - a.importance_score;
    if (sort === 'source') return a.source_name.localeCompare(b.source_name);
    return 0; // date is default order from API
  });

  return (
    <div className="px-10 py-8">
      <div className="mb-8">
        <p className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Category</p>
        <h2 className="text-4xl font-headline font-bold" style={{ color: CAT_COLORS[cat] }}>
          {CAT_LABELS[cat] ?? cat}
        </h2>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-8 flex-wrap">
        <div className="flex bg-surface-container-high rounded-lg p-1 gap-1">
          {TIME_OPTIONS.map(opt => (
            <button
              key={opt.days}
              onClick={() => setDays(opt.days)}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-all ${
                days === opt.days ? 'bg-surface-container-highest text-primary' : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
        <div className="flex bg-surface-container-high rounded-lg p-1 gap-1">
          {SORT_OPTIONS.map(opt => (
            <button
              key={opt}
              onClick={() => setSort(opt)}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-all capitalize ${
                sort === opt ? 'bg-surface-container-highest text-secondary' : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
        <div className="ml-auto flex items-center text-sm text-on-surface-variant">
          <span>{sorted.length} items</span>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48 gap-3 text-on-surface-variant">
          <div className="w-8 h-8 border-3 border-surface-container-highest border-t-primary rounded-full animate-spin" />
          <span className="text-sm animate-pulse">Loading {CAT_LABELS[cat]}...</span>
        </div>
      ) : sorted.length === 0 ? (
        <div className="text-center py-16 text-on-surface-variant">
          <p className="text-lg">No {CAT_LABELS[cat]} data in the selected period.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sorted.map((item, idx) => (
            <div key={idx}>
              <div onClick={() => setExpanded(expanded === idx ? null : idx)} className="cursor-pointer">
                <NewsCard item={item} />
              </div>
              {expanded === idx && (
                <div className="bg-surface-container-highest px-6 py-4 rounded-b-xl -mt-1 border-t border-outline-variant/10 text-sm text-on-surface-variant leading-relaxed">
                  {item.description}
                  <a href={item.source_url} target="_blank" rel="noreferrer" className="ml-3 text-secondary hover:underline">
                    Open source ↗
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
