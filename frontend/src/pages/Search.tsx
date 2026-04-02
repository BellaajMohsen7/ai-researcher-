import { useState } from 'react';
import { api, CATEGORIES, CAT_LABELS, highlight } from '../api';
import type { NewsItem } from '../types';
import { Search as SearchIcon, Filter } from 'lucide-react';
import NewsCard from '../components/NewsCard';

export default function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<(NewsItem & { _category: string; _date: string })[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [catFilter, setCatFilter] = useState<string>('');

  const doSearch = async (q: string) => {
    if (q.trim().length < 2) return;
    setLoading(true);
    setSearched(true);
    const res = await api.search(q);
    // Apply the highlight transformation on result text
    const highlighted = (res?.results ?? []).map((item: NewsItem & { _category: string; _date: string }) => ({
      ...item,
      name: highlight(item.name, q),
      description: highlight(item.description, q),
    }));
    setResults(highlighted);
    setLoading(false);
  };

  const filtered = catFilter ? results.filter(r => r._category === catFilter) : results;

  return (
    <div className="px-10 py-8">
      <div className="mb-8">
        <p className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Search</p>
        <h2 className="text-4xl font-headline font-bold">Find Intelligence</h2>
      </div>

      {/* Search Bar */}
      <div className="relative mb-6">
        <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant pointer-events-none" />
        <input
          type="text"
          value={query}
          className="w-full bg-surface-container-high border border-outline-variant/20 focus:border-primary/50 focus:outline-none rounded-xl pl-12 pr-4 py-4 text-on-surface placeholder-on-surface-variant text-lg transition-colors"
          placeholder="Search AI news... (e.g. llama, gpt, fine-tuning)"
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && doSearch(query)}
        />
        <button
          onClick={() => doSearch(query)}
          className="absolute right-3 top-1/2 -translate-y-1/2 btn-primary py-2 px-4 text-sm"
        >
          Search
        </button>
      </div>

      {/* Category Filter */}
      {searched && results.length > 0 && (
        <div className="flex items-center gap-3 mb-6 flex-wrap">
          <Filter className="w-4 h-4 text-on-surface-variant" />
          <button
            onClick={() => setCatFilter('')}
            className={`px-3 py-1 rounded-lg text-sm transition-all ${!catFilter ? 'text-primary bg-primary/10' : 'text-on-surface-variant hover:text-on-surface'}`}
          >
            All ({results.length})
          </button>
          {CATEGORIES.filter(cat => results.some(r => r._category === cat)).map(cat => (
            <button
              key={cat}
              onClick={() => setCatFilter(cat === catFilter ? '' : cat)}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${catFilter === cat ? 'text-primary bg-primary/10' : 'text-on-surface-variant hover:text-on-surface'}`}
            >
              {CAT_LABELS[cat]} ({results.filter(r => r._category === cat).length})
            </button>
          ))}
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center h-32 gap-3 text-on-surface-variant">
          <div className="w-6 h-6 border-2 border-surface-container-highest border-t-primary rounded-full animate-spin" />
          <span className="text-sm animate-pulse">Searching...</span>
        </div>
      ) : searched && filtered.length === 0 ? (
        <div className="text-center py-16 text-on-surface-variant">
          <p>No results for <span className="text-primary">"{query}"</span></p>
          <p className="text-sm text-outline-variant mt-2">Try a different search term or collect more data.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {filtered.map((item, idx) => (
            <div key={idx}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs text-on-surface-variant">{CAT_LABELS[item._category]}</span>
                <span className="text-xs text-outline-variant">·</span>
                <span className="text-xs text-outline-variant">{item._date}</span>
              </div>
              <NewsCard item={item} highlightText={query} />
            </div>
          ))}
        </div>
      )}

      {!searched && (
        <div className="text-center py-20 text-on-surface-variant">
          <SearchIcon className="w-16 h-16 mx-auto mb-4 text-surface-container-highest" />
          <p>Type above and press Enter to search across all collected AI news.</p>
        </div>
      )}
    </div>
  );
}
