import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import UploadScreen from './screens/UploadScreen'
import CopilotScreen from './screens/CopilotScreen'
import AssetScreen from './screens/AssetScreen'
import MaintenanceScreen from './screens/MaintenanceScreen'
import ComplianceScreen from './screens/ComplianceScreen'
import NotifyScreen from './screens/NotifyScreen'

import KnowledgeCaptureScreen from './screens/KnowledgeCaptureScreen'

const SCREENS = {
  upload:      { title: 'Document Upload',   component: UploadScreen },
  copilot:     { title: 'AI Copilot',        component: CopilotScreen },
  asset:       { title: 'Asset Explorer',    component: AssetScreen },
  maintenance: { title: 'Maintenance Intel', component: MaintenanceScreen },
  compliance:  { title: 'Compliance Intel',  component: ComplianceScreen },
  notify:      { title: 'Notifications',     component: NotifyScreen },
  capture:     { title: 'Knowledge Capture', component: KnowledgeCaptureScreen },
}

// Width in px matching the Tailwind classes used in Sidebar
const SIDEBAR_EXPANDED  = 256  // w-64
const SIDEBAR_COLLAPSED = 68   // w-[68px]

export default function App() {
  const [active, setActive]       = useState('copilot')
  const [collapsed, setCollapsed] = useState(false)

  const { title, component: Screen } = SCREENS[active] ?? SCREENS.copilot
  const sidebarWidth = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED

  return (
    <div className="min-h-screen bg-gray-50 selection:bg-black selection:text-white">
      <Sidebar
        active={active}
        onNavigate={setActive}
        notifyCount={3}
        collapsed={collapsed}
        onToggle={() => setCollapsed(c => !c)}
      />

      {/* Main content shifts with the sidebar */}
      <div
        className="transition-all duration-300 ease-in-out"
        style={{ marginLeft: sidebarWidth }}
      >
        <Header screenTitle={title} sidebarWidth={sidebarWidth} />
        <main className="pt-20 pb-10 min-h-screen">
          <div className="p-8 max-w-5xl mx-auto">
            <Screen />
          </div>
        </main>
      </div>
    </div>
  )
}
