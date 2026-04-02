import { useState, useEffect, useCallback } from 'react';
import { api, CATEGORIES, CAT_LABELS, CAT_COLORS } from '../api';
import type { DailyData, NewsItem } from '../types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity, RefreshCw } from 'lucide-react';
import NewsCard from '../components/NewsCard';

export default function Dashboard() {
  const [data, setData] = useState<DailyData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getToday();
      setData(result);
    } catch { /* empty */ } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000); // auto-refresh every 5 min
    return () => clearInterval(interval);
  }, [fetchData]);

  const allItems: NewsItem[] = data
    ? CATEGORIES.flatMap(cat => (data[cat] || []).map((item: NewsItem) => ({ ...item, _cat: cat })))
        .sort((a, b) => b.importance_score - a.importance_score)
    : [];

  const chartData = CATEGORIES.map(cat => ({
    name: CAT_LABELS[cat],
    count: data?.[cat]?.length ?? 0,
    color: CAT_COLORS[cat],
  }));

  return (
    <div className="px-10 py-8">
      {/* Header */}
      <div className="flex justify-between items-end mb-10">
        <div>
          <p className="text-secondary font-headline tracking-widest text-xs uppercase mb-1">Intelligence Briefing</p>
          <h2 className="text-4xl font-headline font-bold tracking-tight">
            {data ? new Date(data.date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) : 'Loading...'}
          </h2>
        </div>
        <button onClick={fetchData} className="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors text-sm">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-primary' : ''}`} />
          Sync
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <div className="w-10 h-10 border-4 border-surface-container-highest border-t-primary rounded-full animate-spin" />
          <p className="text-on-surface-variant animate-pulse text-sm">Gathering intelligence streams...</p>
        </div>
      ) : !data ? (
        <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant gap-3">
          <p className="text-lg">No data collected yet today.</p>
          <p className="text-sm text-outline-variant">Collection runs at 7 AM. Trigger manually via Settings.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Executive Summary */}
          {data.executive_summary && (
            <section className="bg-surface-container-high p-7 rounded-2xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-[80px] -mr-20 -mt-20 pointer-events-none group-hover:bg-primary/8 transition-all duration-700" />
              <div className="flex items-center gap-2 text-primary mb-3">
                <Activity className="w-4 h-4" />
                <span className="font-headline font-semibold text-sm uppercase tracking-widest">Executive Summary</span>
              </div>
              <p className="text-on-surface leading-relaxed text-lg max-w-4xl relative z-10">{data.executive_summary}</p>
            </section>
          )}

          {/* 6 Category KPIs */}
          <div className="grid grid-cols-3 gap-4">
            {CATEGORIES.map(cat => (
              <div key={cat} className="bg-surface-container-high p-5 rounded-xl">
                <p className="text-xs text-on-surface-variant font-body uppercase tracking-widest mb-2">{CAT_LABELS[cat]}</p>
                <p className="text-3xl font-headline font-bold" style={{ color: CAT_COLORS[cat] }}>
                  {data[cat]?.length ?? 0}
                </p>
              </div>
            ))}
          </div>

          {/* Bar Chart */}
          <section className="bg-surface-container-high p-6 rounded-2xl">
            <h3 className="font-headline font-semibold text-base mb-5 text-on-surface-variant uppercase tracking-widest text-xs">Items per Category</h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fill: '#a8abb3', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#a8abb3', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#151a21', border: '1px solid #44484f30', borderRadius: 8, color: '#f1f3fc' }}
                  cursor={{ fill: 'rgba(73,244,200,0.05)' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </section>

          {/* All Items Feed */}
          <section>
            <h3 className="font-headline font-bold text-2xl mb-5">Latest Discoveries</h3>
            <div className="grid grid-cols-2 gap-4">
              {allItems.map((item, idx) => (
                <NewsCard key={idx} item={item} />
              ))}
            </div>
            {allItems.length === 0 && (
              <p className="text-on-surface-variant text-center py-12">No items collected yet today.</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
