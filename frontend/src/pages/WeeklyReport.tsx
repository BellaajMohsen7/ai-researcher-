import { useState, useEffect } from 'react';
import { api, CATEGORIES, CAT_LABELS, CAT_COLORS } from '../api';
import type { WeeklyReport as WR, NewsItem } from '../types';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis } from 'recharts';
import { ChevronDown, ChevronRight } from 'lucide-react';
import NewsCard from '../components/NewsCard';

export default function WeeklyReport() {
  const [report, setReport] = useState<WR | null>(null);
  const [loading, setLoading] = useState(true);
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});

  useEffect(() => {
    api.getWeeklyLatest().then(r => { setReport(r); setLoading(false); });
  }, []);

  const toggle = (key: string) => setOpenSections(s => ({ ...s, [key]: !s[key] }));

  if (loading) return (
    <div className="flex items-center justify-center h-full text-on-surface-variant gap-3">
      <div className="w-8 h-8 border-4 border-surface-container-highest border-t-primary rounded-full animate-spin" />
      <span className="animate-pulse text-sm">Loading weekly intelligence report...</span>
    </div>
  );

  if (!report) return (
    <div className="flex flex-col items-center justify-center h-full text-on-surface-variant gap-3">
      <p className="text-lg">No weekly report available yet.</p>
      <p className="text-sm text-outline-variant">Reports generate every Sunday at 8 AM, or trigger in Settings.</p>
    </div>
  );

  const pieData = CATEGORIES.map(cat => ({
    name: CAT_LABELS[cat],
    value: report.stats?.total_items_by_category?.[cat] ?? 0,
    color: CAT_COLORS[cat],
  })).filter(d => d.value > 0);

  const lineData = (report.daily_summaries ?? []).map((d: { date: string; total: number }) => ({
    date: d.date?.slice(5),
    items: d.total,
  }));

  const analysis = report.ai_analysis ?? {};
  const trendingTags = report.trending_tags ?? [];

  return (
    <div className="px-10 py-8 space-y-8">
      <div>
        <p className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Intelligence Report</p>
        <h2 className="text-4xl font-headline font-bold">Weekly Briefing</h2>
        <p className="text-on-surface-variant text-sm mt-1">
          {report.stats?.date_range?.start} → {report.stats?.date_range?.end} · {report.stats?.total_items ?? 0} total items
        </p>
      </div>

      {/* Executive Summary */}
      {analysis.executive_summary && (
        <section className="bg-secondary/10 border border-secondary/20 p-7 rounded-2xl">
          <h3 className="text-secondary font-headline font-semibold text-sm uppercase tracking-widest mb-3">Executive Summary</h3>
          <p className="text-on-surface leading-relaxed">{analysis.executive_summary}</p>
        </section>
      )}

      {/* Key Trends */}
      {analysis.key_trends && analysis.key_trends.length > 0 && (
        <section className="bg-surface-container-high p-6 rounded-2xl">
          <h3 className="font-headline font-bold text-xl mb-4">Key Trends</h3>
          <ul className="space-y-2">
            {analysis.key_trends.map((trend: string, i: number) => (
              <li key={i} className="flex items-start gap-3 text-on-surface-variant">
                <span className="text-primary mt-0.5">→</span>
                <span>{trend}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6">
        {lineData.length > 0 && (
          <section className="bg-surface-container-high p-6 rounded-2xl">
            <h3 className="font-headline font-semibold text-sm uppercase tracking-widest text-on-surface-variant mb-4">Items per Day</h3>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={lineData}>
                <XAxis dataKey="date" tick={{ fill: '#a8abb3', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#a8abb3', fontSize: 10 }} axisLine={false} tickLine={false} width={30} />
                <Tooltip contentStyle={{ background: '#151a21', border: '1px solid #44484f30', borderRadius: 8, color: '#f1f3fc', fontSize: 12 }} />
                <Line type="monotone" dataKey="items" stroke="#49f4c8" strokeWidth={2} dot={{ fill: '#49f4c8', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </section>
        )}
        {pieData.length > 0 && (
          <section className="bg-surface-container-high p-6 rounded-2xl flex flex-col">
            <h3 className="font-headline font-semibold text-sm uppercase tracking-widest text-on-surface-variant mb-4">Distribution</h3>
            <div className="flex flex-1 items-center gap-4">
              <ResponsiveContainer width={140} height={140}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={35} outerRadius={60} dataKey="value" paddingAngle={2}>
                    {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#151a21', border: 'none', borderRadius: 8, color: '#f1f3fc', fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 text-xs">
                {pieData.map(d => (
                  <div key={d.name} className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ background: d.color }} />
                    <span className="text-on-surface-variant">{d.name}: <span className="text-on-surface font-medium">{d.value}</span></span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Trending Tags Cloud */}
      {trendingTags.length > 0 && (
        <section className="bg-surface-container-high p-6 rounded-2xl">
          <h3 className="font-headline font-bold text-xl mb-4">Trending Tags</h3>
          <div className="flex flex-wrap gap-2">
            {trendingTags.map(({ tag, count }: { tag: string; count: number }) => (
              <span
                key={tag}
                className="px-3 py-1 rounded-full text-tertiary bg-tertiary/10 font-medium"
                style={{ fontSize: `${Math.max(11, Math.min(18, 10 + count / 2))}px` }}
              >
                #{tag}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Top 5 per Category (collapsible) */}
      {CATEGORIES.map(cat => {
        const catItems: NewsItem[] = (report.top_items as any)?.[cat] ?? [];
        if (catItems.length === 0) return null;
        const isOpen = openSections[cat];
        return (
          <section key={cat} className="bg-surface-container-high rounded-2xl overflow-hidden">
            <button
              onClick={() => toggle(cat)}
              className="w-full flex items-center justify-between px-6 py-4 hover:bg-surface-container-highest transition-colors"
            >
              <span className="font-headline font-semibold" style={{ color: CAT_COLORS[cat] }}>{CAT_LABELS[cat]}</span>
              <div className="flex items-center gap-2 text-on-surface-variant text-sm">
                <span>{catItems.length} items</span>
                {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </div>
            </button>
            {isOpen && (
              <div className="px-6 pb-6 space-y-3">
                {catItems.map((item: NewsItem, i: number) => <NewsCard key={i} item={item} />)}
              </div>
            )}
          </section>
        );
      })}

      {/* Daily Timeline */}
      {report.daily_summaries && report.daily_summaries.length > 0 && (
        <section className="bg-surface-container-high p-6 rounded-2xl">
          <h3 className="font-headline font-bold text-xl mb-4">Daily Timeline</h3>
          <div className="relative space-y-6 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-px before:bg-outline-variant/30">
            {report.daily_summaries.map((day: { date: string; total: number; summary: string }, i: number) => (
              <div key={i} className="pl-10 relative">
                <div className="absolute left-0 top-1 w-7 h-7 bg-surface-container-highest rounded-full border border-outline-variant/40 flex items-center justify-center">
                  <span className="text-[9px] font-bold text-primary">{day.total}</span>
                </div>
                <p className="text-xs text-on-surface-variant mb-1">{day.date}</p>
                <p className="text-sm text-on-surface leading-relaxed">{day.summary}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
