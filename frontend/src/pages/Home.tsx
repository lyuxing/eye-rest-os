import { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS } from '../hooks/useTTS'

export function Home() {
  const { speak, activateTTS } = useTTS()
  const { preferences } = useAppStore()
  const [isActivated, setIsActivated] = useState(false)

  // 点击激活TTS
  const handleActivate = () => {
    const success = activateTTS()
    if (success) {
      setIsActivated(true)
      const greeting = preferences.language === 'zh'
        ? '欢迎使用Eye Rest。请选择：1.时讯简报，2.语言学习，3.音频游戏，4.偏好设置'
        : 'Welcome to Eye Rest. Choose: 1.News, 2.Learning, 3.Game, 4.Settings'
      speak(greeting)
    }
  }

  // 键盘激活
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (!isActivated && ['1', '2', '3', '4'].includes(e.key)) {
        handleActivate()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [isActivated])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 bg-gradient-to-b from-blue-50 to-white">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-gray-800 mb-4">Eye Rest</h1>
        <p className="text-xl text-gray-600 mb-8">
          {preferences.language === 'zh' ? '放松双眼，聆听世界' : 'Relax your eyes, listen to the world'}
        </p>
      </div>

      {/* TTS激活提示 */}
      {!isActivated && (
        <div className="mb-8">
          <button
            onClick={handleActivate}
            className="px-8 py-4 bg-blue-500 text-white rounded-xl text-lg font-semibold hover:bg-blue-600 transition-colors shadow-lg hover:shadow-xl"
          >
            {preferences.language === 'zh' ? '🔊 点击开始语音' : '🔊 Click to Start Audio'}
          </button>
          <p className="mt-4 text-gray-500 text-sm">
            {preferences.language === 'zh'
              ? '浏览器需要用户交互才能播放音频'
              : 'Browser requires user interaction for audio'}
          </p>
        </div>
      )}

      {/* 菜单选项 */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-blue-100 hover:border-blue-300 transition-colors cursor-pointer"
             onClick={() => isActivated && speak(preferences.language === 'zh' ? '时讯简报' : 'News Brief')}>
          <div className="text-4xl font-bold text-blue-600 mb-2">1</div>
          <div className="text-gray-700">
            {preferences.language === 'zh' ? '时讯简报' : 'News Brief'}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-green-100 hover:border-green-300 transition-colors cursor-pointer"
             onClick={() => isActivated && speak(preferences.language === 'zh' ? '语言学习' : 'Language Learning')}>
          <div className="text-4xl font-bold text-green-600 mb-2">2</div>
          <div className="text-gray-700">
            {preferences.language === 'zh' ? '语言学习' : 'Language Learning'}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-purple-100 hover:border-purple-300 transition-colors cursor-pointer"
             onClick={() => isActivated && speak(preferences.language === 'zh' ? '音频游戏' : 'Audio Game')}>
          <div className="text-4xl font-bold text-purple-600 mb-2">3</div>
          <div className="text-gray-700">
            {preferences.language === 'zh' ? '音频游戏' : 'Audio Game'}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-gray-200 hover:border-gray-400 transition-colors cursor-pointer"
             onClick={() => isActivated && speak(preferences.language === 'zh' ? '偏好设置' : 'Settings')}>
          <div className="text-4xl font-bold text-gray-400 mb-2">4</div>
          <div className="text-gray-700">
            {preferences.language === 'zh' ? '偏好设置' : 'Settings'}
          </div>
        </div>
      </div>

      <p className="mt-12 text-gray-500">
        {isActivated
          ? (preferences.language === 'zh' ? '按数字键 1-4 进行选择' : 'Press 1-4 to select')
          : (preferences.language === 'zh' ? '按任意数字键开始' : 'Press any number to start')}
      </p>

      {/* 状态指示 */}
      {isActivated && (
        <div className="mt-4 flex items-center gap-2 text-green-600">
          <span className="animate-pulse">🔊</span>
          <span className="text-sm">{preferences.language === 'zh' ? '语音已激活' : 'Audio activated'}</span>
        </div>
      )}
    </div>
  )
}
