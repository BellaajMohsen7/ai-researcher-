import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { BrainCircuit, LayoutDashboard, Database, Wrench, BookOpen, Zap, Briefcase, BarChart2, Search, Settings, ChevronLeft, ChevronRight } from 'lucide-react';
import { CAT_LABELS } from '../api';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, exact: true },
  { to: '/category/ai_models', label: CAT_LABELS.ai_models, icon: Database },
  { to: '/category/frameworks', label: CAT_LABELS.frameworks, icon: Zap },
  { to: '/category/tools', label: CAT_LABELS.tools, icon: Wrench },
  { to: '/category/courses', label: CAT_LABELS.courses, icon: BookOpen },
  { to: '/category/skills', label: CAT_LABELS.skills, icon: BrainCircuit },
  { to: '/category/opportunities', label: CAT_LABELS.opportunities, icon: Briefcase },
  { to: '/report', label: 'Weekly Report', icon: BarChart2, divider: true },
  { to: '/search', label: 'Search', icon: Search },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-background text-on-surface overflow-hidden">
      <aside className={`bg-surface-container-low flex flex-col py-6 shrink-0 transition-all duration-300 ${collapsed ? 'w-20' : 'w-64'}`}>
        <div className={`px-6 mb-10 flex items-center ${collapsed ? 'justify-center px-0' : 'space-x-3'}`}>
          <div className="w-8 h-8 rounded bg-gradient-primary flex items-center justify-center shrink-0">
            <BrainCircuit className="w-5 h-5 text-surface" />
          </div>
          {!collapsed && <h1 className="font-headline font-bold text-xl tracking-tight whitespace-nowrap">AI Observer</h1>}
        </div>
        <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon, exact, divider }) => (
            <div key={to}>
              {divider && <div className="my-3 border-t border-outline-variant/20" />}
              <NavLink
                to={to}
                end={exact}
                className={({ isActive }) =>
                  `flex items-center rounded-lg text-sm font-medium transition-all ${
                    collapsed ? 'justify-center p-2.5 space-x-0' : 'px-4 py-2.5 space-x-3'
                  } ${
                    isActive
                      ? 'bg-surface-container-highest text-primary'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
                  }`
                }
                title={collapsed ? label : undefined}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {!collapsed && <span className="whitespace-nowrap">{label}</span>}
              </NavLink>
            </div>
          ))}
        </nav>
        <div className="px-4 mt-auto pt-4 border-t border-outline-variant/20">
          <button 
            onClick={() => setCollapsed(!collapsed)} 
            className={`w-full flex items-center rounded-lg text-sm font-medium transition-all text-on-surface-variant hover:text-on-surface hover:bg-surface-container ${collapsed ? 'justify-center p-2.5' : 'px-4 py-2.5 space-x-3'}`}
            title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {collapsed ? <ChevronRight className="w-4 h-4 shrink-0" /> : <ChevronLeft className="w-4 h-4 shrink-0" />}
            {!collapsed && <span className="whitespace-nowrap">Collapse Sidebar</span>}
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
