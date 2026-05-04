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

function App() {
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

export default App