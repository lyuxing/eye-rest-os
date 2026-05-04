import { useEffect, useState, useRef, useCallback } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS, isTTSActivated } from '../hooks/useTTS'
import { fetchGameList, startGame, makeGameChoice } from '../services/api'
import type { GameInfo, GameSession } from '../services/api'

export function Game() {
  const { gameSession, setGameSession, setPage, preferences } = useAppStore()
  const { speak } = useTTS()
  const [games, setGames] = useState<GameInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [playingGame, setPlayingGame] = useState(false)

  const sessionRef = useRef<GameSession | null>(null)
  const loadingRef = useRef(false)

  const isZh = preferences.language === 'zh'

  useEffect(() => {
    sessionRef.current = gameSession
  }, [gameSession])

  useEffect(() => {
    loadingRef.current = loading
  }, [loading])

  useEffect(() => {
    const loadGames = async () => {
      try {
        const data = await fetchGameList()
        setGames(data)
      } catch {
        setGames([
          { id: 'forest_adventure', title: '森林探险', description: '神秘森林探险', difficulty: 'easy' },
          { id: 'space_station', title: '太空站危机', description: '太空站求生', difficulty: 'medium' },
          { id: 'detective', title: '午夜侦探', description: '古堡探案', difficulty: 'hard' }
        ])
      }
    }
    loadGames()
  }, [])

  // 播放场景内容（叙述 + 选项）
  const speakScene = useCallback((session: GameSession) => {
    if (!isTTSActivated()) return

    // 先播报叙述
    let fullText = session.narration

    // 如果不是结束场景，播报选项
    if (!session.is_end && session.choices.length > 0) {
      fullText += isZh ? '。你的选择是：' : '. Your choices are: '
      session.choices.forEach((choice) => {
        fullText += `${isZh ? '按' : 'Press'} ${choice.key}, ${choice.text}。`
      })
    }

    speak(fullText)
  }, [isZh, speak])

  // 游戏列表键盘处理
  useEffect(() => {
    if (playingGame) return

    const handleKey = (e: KeyboardEvent) => {
      const key = e.key
      if (!['1', '2', '3', '4'].includes(key)) return

      const idx = parseInt(key) - 1
      if (idx >= 0 && idx < games.length) {
        handleSelectGame(idx)
      } else if (key === '4') {
        setPage('home')
      }
    }

    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [playingGame, games, setPage])

  // 游戏进行中键盘处理
  useEffect(() => {
    if (!playingGame) return

    const handleKey = async (e: KeyboardEvent) => {
      const key = e.key
      if (!['1', '2', '3', '4'].includes(key)) return

      if (key === '4') {
        setPlayingGame(false)
        setGameSession(null)
        sessionRef.current = null
        speak(isZh ? '返回游戏列表' : 'Back to game list')
        return
      }

      const currentSession = sessionRef.current
      if (currentSession && !currentSession.is_end && !loadingRef.current) {
        await handleChoice(key)
      }
    }

    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [playingGame, isZh, setGameSession, speak])

  const handleSelectGame = async (index: number) => {
    if (index < 0 || index >= games.length || loading) return

    const game = games[index]
    setLoading(true)

    try {
      const session = await startGame(game.id)
      setGameSession(session)
      sessionRef.current = session
      setPlayingGame(true)

      // 播放场景内容（包括选项）
      speakScene(session)
    } catch (err) {
      console.error('Failed to start game:', err)
      speak(isZh ? '游戏启动失败' : 'Failed to start game')
    } finally {
      setLoading(false)
    }
  }

  const handleChoice = useCallback(async (choice: string) => {
    const currentSession = sessionRef.current
    if (!currentSession || loadingRef.current) return

    setLoading(true)
    loadingRef.current = true

    try {
      console.log('Making choice:', choice, 'for session:', currentSession.session_id)
      const newSession = await makeGameChoice(currentSession.session_id, choice)
      console.log('New session:', newSession)

      setGameSession(newSession)
      sessionRef.current = newSession

      // 播放场景内容（包括选项）
      speakScene(newSession)

      if (newSession.is_end) {
        setTimeout(() => {
          const endMsg = isZh
            ? `游戏结束！${newSession.result === 'success' ? '恭喜你成功通关！' : '游戏结束，再接再厉！'}`
            : `Game Over! ${newSession.result === 'success' ? 'Congratulations!' : 'Try again!'}`
          speak(endMsg)
        }, 3000) // 等待叙述播完
      }
    } catch (err) {
      console.error('Choice failed:', err)
      speak(isZh ? '选择失败，请重试' : 'Choice failed, please try again')
    } finally {
      setLoading(false)
      loadingRef.current = false
    }
  }, [isZh, setGameSession, speak, speakScene])

  // 重新播报当前场景
  const replayScene = useCallback(() => {
    if (sessionRef.current) {
      speakScene(sessionRef.current)
    }
  }, [speakScene])

  const difficultyColors: Record<string, string> = {
    easy: 'bg-green-100 text-green-700',
    medium: 'bg-yellow-100 text-yellow-700',
    hard: 'bg-red-100 text-red-700'
  }

  const difficultyLabels: Record<string, string> = {
    easy: isZh ? '简单' : 'Easy',
    medium: isZh ? '中等' : 'Medium',
    hard: isZh ? '困难' : 'Hard'
  }

  // 游戏列表视图
  if (!playingGame || !gameSession) {
    return (
      <div className="flex flex-col min-h-screen bg-gradient-to-b from-orange-50 to-white pb-32">
        <div className="flex-1 p-8">
          <div className="max-w-lg mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                {isZh ? '音频游戏' : 'Audio Games'}
              </h1>
              <p className="text-gray-500">{isZh ? '选择一个游戏开始' : 'Choose a game to play'}</p>
            </div>

            <div className="space-y-4">
              {games.map((game, idx) => (
                <button
                  key={game.id}
                  onClick={() => handleSelectGame(idx)}
                  className="w-full bg-white rounded-xl shadow-lg p-6 text-left hover:shadow-xl transition-all border-l-4 border-orange-300 hover:border-orange-500"
                  disabled={loading}
                >
                  <div className="flex items-center gap-4">
                    <div className="text-3xl font-bold text-orange-500">{idx + 1}</div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-gray-800">{game.title}</h3>
                      <p className="text-sm text-gray-500">{game.description}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${difficultyColors[game.difficulty]}`}>
                      {difficultyLabels[game.difficulty]}
                    </span>
                  </div>
                </button>
              ))}
            </div>

            <div className="mt-8 bg-gray-100 rounded-xl p-4 text-center">
              <p className="text-gray-500">
                {isZh ? '按数字键选择游戏，按4退出' : 'Press number to select, press 4 to exit'}
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 游戏进行中视图
  return (
    <div className="flex flex-col min-h-screen bg-gray-900 text-white pb-32">
      <div className="flex-1 p-8">
        <div className="max-w-lg mx-auto">
          <div className="text-center mb-6">
            <span className="text-sm text-gray-400">
              {gameSession.title || games.find(g => g.id === gameSession.game_id)?.title}
            </span>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 mb-6">
            <p className="text-lg leading-relaxed">{gameSession.narration}</p>
          </div>

          {!gameSession.is_end && gameSession.choices.length > 0 && (
            <div className="space-y-3">
              {gameSession.choices.map((choice, idx) => (
                <button
                  key={idx}
                  onClick={() => handleChoice(choice.key)}
                  className="w-full bg-gray-700 rounded-lg p-4 text-left hover:bg-gray-600 transition-colors flex items-center gap-3 disabled:opacity-50"
                  disabled={loading}
                >
                  <span className="text-2xl font-bold text-orange-400">{choice.key}</span>
                  <span className="flex-1">{choice.text}</span>
                </button>
              ))}
            </div>
          )}

          {gameSession.is_end && (
            <div className="text-center mt-8">
              <div className="text-4xl mb-4">
                {gameSession.result === 'success' ? '🎉' : '💪'}
              </div>
              <p className="text-xl mb-4">
                {gameSession.result === 'success'
                  ? (isZh ? '恭喜通关！' : 'Congratulations!')
                  : (isZh ? '再接再厉！' : 'Try again!')}
              </p>
              <button
                onClick={() => {
                  setPlayingGame(false)
                  setGameSession(null)
                  sessionRef.current = null
                }}
                className="px-6 py-3 bg-orange-500 rounded-lg hover:bg-orange-600 transition-colors"
              >
                {isZh ? '返回游戏列表' : 'Back to Games'}
              </button>
            </div>
          )}

          {/* 重播按钮 */}
          {!gameSession.is_end && (
            <div className="mt-6 text-center">
              <button
                onClick={replayScene}
                className="px-6 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors"
              >
                🔊 {isZh ? '重新播报' : 'Replay'}
              </button>
            </div>
          )}

          <div className="mt-8 bg-gray-800 rounded-xl p-4">
            <p className="text-center text-gray-400 text-sm">
              {gameSession.is_end
                ? (isZh ? '点击按钮返回' : 'Click button to go back')
                : (isZh ? '按数字键选择，按4退出' : 'Press number to choose, press 4 to exit')}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}