import {
  UploadCloud, MessageSquare, Map, Wrench,
  ShieldCheck, Bell, Activity
} from 'lucide-react'

const NAV = [
  { id: 'upload',      icon: UploadCloud,   label: 'Document Upload',  sub: 'Upload, auto-process' },
  { id: 'copilot',     icon: MessageSquare, label: 'AI Copilot',       sub: 'Ask + cited answers' },
  { id: 'asset',       icon: Map,           label: 'Asset Explorer',   sub: 'Interactive P&ID map' },
  { id: 'maintenance', icon: Wrench,        label: 'Maintenance Intel',sub: 'Predictive + RCA' },
  { id: 'compliance',  icon: ShieldCheck,   label: 'Compliance Intel', sub: 'Gap checks + audits' },
  { id: 'notify',      icon: Bell,          label: 'Notifications',    sub: 'Proactive alert feed' },
]

export default function Sidebar({ active, onNavigate, notifyCount = 0 }) {
  return (
    <aside className="fixed top-0 left-0 h-screen w-64 glass-panel border-r-0 border-r-surface-200 flex flex-col z-40 bg-white/80">
      {/* Logo */}
      <div className="px-6 py-8 border-b border-surface-200 relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-r from-accent-cyan/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
        <div className="flex items-center gap-3 relative z-10">
          <div className="w-8 h-8 rounded-lg bg-surface-50 border border-surface-200 flex items-center justify-center shadow-[0_0_15px_rgba(2,132,199,0.1)] group-hover:neon-border-cyan transition-all duration-300">
            <Activity size={18} className="text-accent-cyan group-hover:neon-text-cyan transition-all" />
          </div>
          <div>
            <div className="text-[13px] font-display font-bold text-gray-900 tracking-wide uppercase leading-tight">Industrial</div>
            <div className="text-[10px] font-mono text-accent-cyan uppercase tracking-widest leading-tight mt-0.5">Intelligence</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
        {NAV.map(({ id, icon: Icon, label, sub }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className={`
                w-full flex items-center gap-3 px-3 py-3 text-left rounded-xl transition-all duration-300 relative group
                ${isActive
                  ? 'bg-accent-cyan/10 text-accent-cyan shadow-[inset_0_0_15px_rgba(2,132,199,0.05)] border border-accent-cyan/20'
                  : 'text-gray-600 hover:bg-surface-100/80 hover:text-gray-900 border border-transparent hover:border-surface-200'}
              `}
            >
              {isActive && (
                <div className="absolute -left-3 top-1/2 -translate-y-1/2 w-1 h-8 bg-accent-cyan rounded-r-full shadow-[0_0_10px_rgba(2,132,199,0.5)]"></div>
              )}
              <Icon size={18} className={`shrink-0 transition-all duration-300 ${isActive ? 'neon-text-cyan' : 'group-hover:text-gray-700 group-hover:scale-110'}`} />
              <div className="min-w-0">
                <div className={`text-sm font-medium leading-tight truncate transition-colors ${isActive ? 'text-gray-900' : ''}`}>{label}</div>
                <div className={`text-[11px] leading-tight truncate mt-0.5 ${isActive ? 'text-accent-cyan' : 'text-gray-500'}`}>
                  {sub}
                </div>
              </div>
              {id === 'notify' && notifyCount > 0 && (
                <span className="ml-auto shrink-0 w-5 h-5 rounded-md bg-accent-amber/10 border border-accent-amber text-accent-amber text-[10px] flex items-center justify-center font-bold shadow-[0_0_10px_rgba(217,119,6,0.15)]">
                  {notifyCount > 9 ? '9+' : notifyCount}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-surface-200 bg-surface-50/50">
        <div className="flex items-center justify-between">
          <div className="text-[10px] font-mono text-gray-500 uppercase tracking-wider">ET Hackathon</div>
          <div className="text-[10px] font-mono text-accent-cyan bg-accent-cyan/10 px-2 py-0.5 rounded border border-accent-cyan/20">v0.3.0</div>
        </div>
      </div>
    </aside>
  )
}
