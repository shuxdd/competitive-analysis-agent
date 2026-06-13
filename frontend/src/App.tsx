import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { queryClient } from '@/lib/queryClient'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { MainLayout } from '@/layouts/MainLayout'
import Dashboard from '@/pages/dashboard'
import CompetitorList from '@/pages/competitors'
import AnalysisList from '@/pages/analysis'
import AnalysisDetail from '@/pages/analysis/[id]'
import ReportList from '@/pages/reports'
import ReportDetail from '@/pages/reports/[id]'
import QA from '@/pages/qa'
import LoginPage from '@/pages/login'
import RegisterPage from '@/pages/register'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, token } = useAuth()
  if (!token || !user) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function AppRoutes() {
  const { token } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={token ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route path="/register" element={token ? <Navigate to="/" replace /> : <RegisterPage />} />
      <Route path="/" element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="competitors" element={<CompetitorList />} />
        <Route path="analysis" element={<AnalysisList />} />
        <Route path="analysis/:id" element={<AnalysisDetail />} />
        <Route path="reports" element={<ReportList />} />
        <Route path="reports/:id" element={<ReportDetail />} />
        <Route path="qa" element={<QA />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  )
}

export default App
