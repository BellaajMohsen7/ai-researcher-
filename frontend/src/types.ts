export interface NewsItem {
  name: string;
  description: string;
  source_url: string;
  source_name: string;
  importance_score: number;
  tags: string[];
}

export interface DailyData {
  date: string;
  executive_summary?: string;
  ai_models?: NewsItem[];
  frameworks?: NewsItem[];
  tools?: NewsItem[];
  courses?: NewsItem[];
  skills?: NewsItem[];
  opportunities?: NewsItem[];
  stats: {
    total_items: number;
    llm_provider_used?: string;
  };
  [key: string]: any; 
}

export interface WeeklyReport {
  week_id?: string;
  generated_at?: string;
  stats?: {
    days_collected: number;
    date_range: { start: string; end: string };
    total_items_by_category: Record<string, number>;
    total_items: number;
  };
  trending_tags?: { tag: string; count: number }[];
  top_items?: Record<string, NewsItem[]>;
  ai_analysis?: {
    executive_summary?: string;
    key_trends?: string[];
    model_highlights?: string;
    tools_frameworks?: string;
    learning_opportunities?: string;
    career_outlook?: string;
    watch_next_week?: string;
  };
  daily_summaries?: { date: string; total: number; summary: string }[];
}
