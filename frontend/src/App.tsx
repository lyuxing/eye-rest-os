import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/useAuthStore'
import { useAppStore } from './store/useAppStore'
import { Navigation } from './components/Navigation'
import { Home } from './pages/Home'
import { News } from './pages/News'
import { DailyPhrase } from './pages/DailyPhrase'
import { Speech } from './pages/Speech'
import { Dialogue } from './pages/Dialogue'
import { Learning } from './pages/Learning'
import { Game } from './pages/Game'
import { Settings } from './pages/Settings'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Onboarding } from './pages/Onboarding'

// 认证守卫组件
function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Onboarding守卫 - 检查是否完成初始化
function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user && !user.onboarding_completed) {
    return <Navigate to="/onboarding" replace />
  }

  return <>{children}</>
}

// 主应用组件 - 使用原来的页面导航
function MainApp() {
  const { currentPage } = useAppStore()

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home />
      case 'news':
        return <News />
      case 'phrase':
        return <DailyPhrase />
      case 'speech':
        return <Speech />
      case 'dialogue':
        return <Dialogue />
      case 'learning':
        return <Learning />
      case 'game':
        return <Game />
      case 'settings':
        return <Settings />
      default:
        return <Home />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {renderPage()}
      <Navigation />
    </div>
  )
}

function App() {
  const { setLoading } = useAuthStore()

  // 初始化时检查认证状态
  useEffect(() => {
    // Zustand persist会自动恢复状态，只需标记加载完成
    setLoading(false)
  }, [setLoading])

  return (
    <BrowserRouter>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* 需要认证但未完成onboarding的路由 */}
        <Route
          path="/onboarding"
          element={
            <AuthGuard>
              <Onboarding />
            </AuthGuard>
          }
        />

        {/* 需要完整认证的路由 */}
        <Route
          path="/home"
          element={
            <OnboardingGuard>
              <MainApp />
            </OnboardingGuard>
          }
        />
        <Route
          path="/*"
          element={
            <OnboardingGuard>
              <MainApp />
            </OnboardingGuard>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App