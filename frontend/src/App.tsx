import { Route, Routes } from 'react-router'
import AppShell from './components/AppShell'
import { NotFound } from './components/PageStatus'
import CountryPage from './pages/CountryPage'
import OverviewPage from './pages/OverviewPage'
import PlantPage from './pages/PlantPage'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/country/:name" element={<CountryPage />} />
        <Route path="/plant/:id" element={<PlantPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AppShell>
  )
}
