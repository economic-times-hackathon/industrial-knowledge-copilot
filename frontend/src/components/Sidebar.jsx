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
    <aside className="fixed top-0 left-0 h-screen w-56 bg-surface-800 border-r border-surface-600 flex flex-col z-20">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-surface-600">
        <div className="flex items-center gap-2">
          <Activity size={20} className="text-accent-blue shrink-0" />
          <div>
            <div className="text-xs font-semibold text-white leading-tight">Industrial</div>
            <div className="text-[10px] text-gray-400 leading-tight">Knowledge Intelligence</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2">
        {NAV.map(({ id, icon: Icon, label, sub }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className={`
                w-full flex items-center gap-3 px-4 py-3 text-left transition-colors relative
                ${isActive
                  ? 'bg-accent-blue/10 text-accent-blue border-r-2 border-accent-blue'
                  : 'text-gray-400 hover:bg-surface-700 hover:text-gray-200'}
              `}
            >
              <Icon size={16} className="shrink-0" />
              <div className="min-w-0">
                <div className="text-xs font-medium leading-tight truncate">{label}</div>
                <div className={`text-[10px] leading-tight truncate ${isActive ? 'text-blue-300/70' : 'text-gray-600'}`}>
                  {sub}
                </div>
              </div>
              {id === 'notify' && notifyCount > 0 && (
                <span className="ml-auto shrink-0 w-4 h-4 rounded-full bg-accent-red text-white text-[9px] flex items-center justify-center font-bold">
                  {notifyCount > 9 ? '9+' : notifyCount}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-surface-600">
        <div className="text-[10px] text-gray-600">ET Hackathon 2026</div>
        <div className="text-[10px] text-gray-700">v0.2.0</div>
      </div>
    </aside>
  )
}
