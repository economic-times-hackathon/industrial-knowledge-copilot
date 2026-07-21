import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import UploadScreen from './screens/UploadScreen'
import CopilotScreen from './screens/CopilotScreen'
import AssetScreen from './screens/AssetScreen'
import MaintenanceScreen from './screens/MaintenanceScreen'
import ComplianceScreen from './screens/ComplianceScreen'
import NotifyScreen from './screens/NotifyScreen'

const SCREENS = {
  upload:      { title: 'Document Upload',   component: UploadScreen },
  copilot:     { title: 'AI Copilot',        component: CopilotScreen },
  asset:       { title: 'Asset Explorer',    component: AssetScreen },
  maintenance: { title: 'Maintenance Intel', component: MaintenanceScreen },
  compliance:  { title: 'Compliance Intel',  component: ComplianceScreen },
  notify:      { title: 'Notifications',     component: NotifyScreen },
}

export default function App() {
  const [active, setActive] = useState('copilot')
  const { title, component: Screen } = SCREENS[active] ?? SCREENS.copilot

  return (
    <div className="min-h-screen bg-transparent relative selection:bg-accent-cyan/30 selection:text-accent-cyan">
      <Sidebar active={active} onNavigate={setActive} notifyCount={3} />
      <div className="ml-64 transition-all duration-300">
        <Header screenTitle={title} />
        <main className="pt-20 pb-10 min-h-screen">
          <div className="p-6 max-w-5xl mx-auto relative z-10">
            <Screen />
          </div>
        </main>
      </div>
    </div>
  )
}
