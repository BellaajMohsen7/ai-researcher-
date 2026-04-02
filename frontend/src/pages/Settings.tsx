import { useState, useEffect } from 'react';
import { api } from '../api';
import { Clock, CheckCircle } from 'lucide-react';

interface SchedulerJob {
  id: string;
  name: string;
  next_run: string;
}

interface Stats {
  total_daily_collections: number;
  total_weekly_reports: number;
  latest_collection: string | null;
  available_dates: string[];
}

export default function Settings() {
  const [jobs, setJobs] = useState<SchedulerJob[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    Promise.all([api.getScheduler(), api.getStats()]).then(([sched, st]) => {
      setJobs(sched?.jobs ?? []);
      setStats(st);
      setLoading(false);
    });
  }, []);

  return (
    <div className="px-10 py-8 space-y-8">
      <div>
        <p className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Configuration</p>
        <h2 className="text-4xl font-headline font-bold">Settings</h2>
      </div>


      {/* Scheduler Status */}
      <section className="bg-surface-container-high p-6 rounded-2xl">
        <h3 className="font-headline font-bold text-xl mb-5">Scheduler Status</h3>
        {loading ? (
          <div className="animate-pulse space-y-3">
            <div className="h-12 bg-surface-container-highest rounded-xl" />
            <div className="h-12 bg-surface-container-highest rounded-xl" />
          </div>
        ) : jobs.length === 0 ? (
          <p className="text-on-surface-variant text-sm">No scheduled jobs found.</p>
        ) : (
          <div className="space-y-3">
            {jobs.map(job => (
              <div key={job.id} className="flex items-center justify-between bg-surface-container-highest px-5 py-4 rounded-xl">
                <div className="flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />
                  <div>
                    <p className="font-medium text-on-surface text-sm">{job.name}</p>
                    <p className="text-xs text-on-surface-variant">{job.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-on-surface-variant text-xs">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Next: {job.next_run === 'None' ? 'Not scheduled' : new Date(job.next_run).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Overall Stats */}
      {stats && (
        <section className="bg-surface-container-high p-6 rounded-2xl">
          <h3 className="font-headline font-bold text-xl mb-5">Pipeline Statistics</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-surface-container-highest p-5 rounded-xl">
              <p className="text-xs text-on-surface-variant uppercase tracking-widest mb-2">Daily Collections</p>
              <p className="text-3xl font-headline font-bold text-primary">{stats.total_daily_collections}</p>
            </div>
            <div className="bg-surface-container-highest p-5 rounded-xl">
              <p className="text-xs text-on-surface-variant uppercase tracking-widest mb-2">Weekly Reports</p>
              <p className="text-3xl font-headline font-bold text-secondary">{stats.total_weekly_reports}</p>
            </div>
          </div>

          {stats.latest_collection && (
            <div className="mt-4 flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-primary" />
              <span className="text-on-surface-variant">Latest collection: <span className="text-on-surface">{stats.latest_collection}</span></span>
            </div>
          )}

          {stats.available_dates.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-on-surface-variant uppercase tracking-widest mb-2">Recent Dates</p>
              <div className="flex flex-wrap gap-2">
                {stats.available_dates.map(d => (
                  <span key={d} className="px-3 py-1 bg-surface-container-highest text-on-surface-variant text-xs rounded-lg">{d}</span>
                ))}
              </div>
            </div>
          )}
        </section>
      )}


    </div>
  );
}
