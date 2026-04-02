const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  getToday: () => fetch(`${BASE}/api/news/today`).then(r => r.ok ? r.json() : null),
  getByDate: (date: string) => fetch(`${BASE}/api/news/${date}`).then(r => r.ok ? r.json() : null),
  getCategory: (cat: string, days = 7) => fetch(`${BASE}/api/news/category/${cat}?days=${days}`).then(r => r.json()),
  search: (q: string) => fetch(`${BASE}/api/news/search?q=${encodeURIComponent(q)}`).then(r => r.json()),
  getStats: () => fetch(`${BASE}/api/stats`).then(r => r.json()),
  getWeeklyLatest: () => fetch(`${BASE}/api/reports/weekly/latest`).then(r => r.ok ? r.json() : null),
  listWeeklyReports: () => fetch(`${BASE}/api/reports/weekly`).then(r => r.json()),
  getScheduler: () => fetch(`${BASE}/api/scheduler/status`).then(r => r.json()),
  triggerDaily: () => fetch(`${BASE}/api/trigger/daily`, { method: 'POST' }).then(r => r.json()),
  triggerWeekly: () => fetch(`${BASE}/api/trigger/weekly`, { method: 'POST' }).then(r => r.json()),
};

export const CATEGORIES = ['ai_models', 'frameworks', 'tools', 'courses', 'skills', 'opportunities'] as const;
export type Category = typeof CATEGORIES[number];

export const CAT_LABELS: Record<string, string> = {
  ai_models: 'AI Models',
  frameworks: 'Frameworks',
  tools: 'Tools',
  courses: 'Courses',
  skills: 'Skills',
  opportunities: 'Opportunities',
};

export const CAT_COLORS: Record<string, string> = {
  ai_models: '#49f4c8',
  frameworks: '#58a6ff',
  tools: '#c79eff',
  courses: '#f4a949',
  skills: '#f44949',
  opportunities: '#49f4c8',
};

export function scoreColor(score: number): string {
  if (score >= 8) return 'text-red-400 bg-red-400/10';
  if (score >= 5) return 'text-yellow-400 bg-yellow-400/10';
  return 'text-green-400 bg-green-400/10';
}

export function highlight(text: string, query: string): string {
  if (!query) return text;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<mark class="bg-primary/30 text-primary rounded px-0.5">$1</mark>');
}
