import {
  UploadCloud, MessageSquare, Map, Wrench,
  ShieldCheck, Bell, Activity, ChevronLeft, ChevronRight, Mic
} from 'lucide-react'

const NAV = [
  { id: 'upload',      icon: UploadCloud,   label: 'Document Upload',   sub: 'Upload, auto-process' },
  { id: 'copilot',     icon: MessageSquare, label: 'AI Copilot',        sub: 'Ask + cited answers' },
  { id: 'asset',       icon: Map,           label: 'Asset Explorer',    sub: 'Interactive P&ID map' },
  { id: 'maintenance', icon: Wrench,        label: 'Maintenance Intel', sub: 'Predictive + RCA' },
  { id: 'compliance',  icon: ShieldCheck,   label: 'Compliance Intel',  sub: 'Gap checks + audits' },
  { id: 'notify',      icon: Bell,          label: 'Notifications',     sub: 'Proactive alert feed' },
  { id: 'capture',     icon: Mic,           label: 'Knowledge Capture', sub: 'Record expert knowledge' },
]

export default function Sidebar({ active, onNavigate, notifyCount = 0, collapsed, onToggle }) {
  return (
    <aside
      className={`
        fixed top-0 left-0 h-screen bg-white border-r-2 border-gray-200
        flex flex-col z-40 shadow-sm
        transition-all duration-300 ease-in-out
        ${collapsed ? 'w-[68px]' : 'w-64'}
      `}
    >
      {/* Logo + Toggle */}
      <div className={`flex items-center border-b-2 border-gray-100 h-16 shrink-0 ${collapsed ? 'justify-center px-0' : 'px-4 gap-3'}`}>
        {/* Logo icon */}
        <div className="w-9 h-9 rounded-lg bg-black flex items-center justify-center shrink-0">
          <Activity size={18} className="text-white" />
        </div>

        {/* Title — hidden when collapsed */}
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <div className="text-[13px] font-display font-bold text-black tracking-wide uppercase leading-tight truncate">
              Industrial
            </div>
            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-widest leading-tight mt-0.5">
              Intelligence
            </div>
          </div>
        )}

        {/* Toggle button */}
        <button
          onClick={onToggle}
          className={`
            shrink-0 w-7 h-7 rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100
            flex items-center justify-center text-gray-500 hover:text-black transition-colors
            ${collapsed ? 'absolute -right-3.5 top-[26px] shadow-md bg-white border-2 border-gray-200 z-50' : ''}
          `}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={13} /> : <ChevronLeft size={13} />}
        </button>
      </div>

      {/* Nav */}
      <nav className={`flex-1 overflow-y-auto py-4 space-y-1 ${collapsed ? 'px-2' : 'px-3'}`}>
        {NAV.map(({ id, icon: Icon, label, sub }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              title={collapsed ? label : undefined}
              className={`
                w-full flex items-center text-left rounded-xl transition-all duration-200
                ${collapsed ? 'justify-center px-0 py-3' : 'gap-3 px-3 py-3'}
                ${isActive
                  ? 'bg-black text-white'
                  : 'text-gray-500 hover:bg-gray-100 hover:text-black'}
              `}
            >
              {/* Icon */}
              <div className="relative shrink-0">
                <Icon size={18} className={isActive ? 'text-white' : 'text-gray-600'} />
                {/* Notification dot on icon when collapsed */}
                {collapsed && id === 'notify' && notifyCount > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 rounded-full bg-black text-white text-[8px] flex items-center justify-center font-bold border border-white">
                    {notifyCount > 9 ? '9' : notifyCount}
                  </span>
                )}
              </div>

              {/* Label + sub — only when expanded */}
              {!collapsed && (
                <div className="min-w-0 flex-1">
                  <div className={`text-sm font-semibold leading-tight truncate ${isActive ? 'text-white' : 'text-gray-800'}`}>
                    {label}
                  </div>
                  <div className={`text-[11px] leading-tight truncate mt-0.5 ${isActive ? 'text-gray-300' : 'text-gray-400'}`}>
                    {sub}
                  </div>
                </div>
              )}

              {/* Notification badge — only when expanded */}
              {!collapsed && id === 'notify' && notifyCount > 0 && (
                <span className={`ml-auto shrink-0 min-w-[20px] h-5 px-1 rounded text-[10px] flex items-center justify-center font-bold
                  ${isActive ? 'bg-white text-black' : 'bg-black text-white'}`}>
                  {notifyCount > 9 ? '9+' : notifyCount}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="px-5 py-4 border-t-2 border-gray-100">
          <div className="flex items-center justify-between">
            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">ET Hackathon</div>
            <div className="text-[10px] font-mono text-black bg-gray-100 px-2 py-0.5 rounded border border-gray-200 font-bold">
              v0.3.0
            </div>
          </div>
        </div>
      )}

      {/* Collapsed footer — just version dot */}
      {collapsed && (
        <div className="py-4 flex justify-center border-t-2 border-gray-100">
          <div className="w-2 h-2 rounded-full bg-black" title="v0.3.0" />
        </div>
      )}
    </aside>
  )
}
