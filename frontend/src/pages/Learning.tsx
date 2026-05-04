import { useEffect } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS, isTTSActivated } from '../hooks/useTTS'

export function Learning() {
  const { preferences, setPage } = useAppStore()
  const { speak } = useTTS()

  useEffect(() => {
    if (isTTSActivated()) {
      const text = preferences.language === 'zh'
        ? '语言学习。请选择：1.每日一句，2.每日演讲，3.每日对话，4.返回'
        : 'Language Learning. Choose: 1.Daily Phrase, 2.Daily Speech, 3.Daily Dialogue, 4.Back'
      speak(text)
    }
  }, [])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      const key = e.key
      if (key === '1') setPage('phrase')
      else if (key === '2') setPage('speech')
      else if (key === '3') setPage('dialogue')
      else if (key === '4') setPage('home')
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [setPage])

  const isZh = preferences.language === 'zh'

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 bg-gradient-to-b from-green-50 to-white">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          {isZh ? '语言学习' : 'Language Learning'}
        </h1>
        <p className="text-gray-500">{isZh ? '选择今日学习内容' : 'Choose today\'s content'}</p>
      </div>

      <div className="w-full max-w-lg space-y-4">
        <div className="bg-white rounded-xl shadow-lg p-6 flex items-center gap-4 border-l-4 border-green-500 cursor-pointer hover:shadow-xl transition-all"
             onClick={() => setPage('phrase')}>
          <div className="text-3xl font-bold text-green-600">1</div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-800">{isZh ? '每日一句' : 'Daily Phrase'}</h3>
            <p className="text-sm text-gray-500">{isZh ? '经典短语与用法' : 'Classic phrases and usage'}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 flex items-center gap-4 border-l-4 border-blue-500 cursor-pointer hover:shadow-xl transition-all"
             onClick={() => setPage('speech')}>
          <div className="text-3xl font-bold text-blue-600">2</div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-800">{isZh ? '每日演讲' : 'Daily Speech'}</h3>
            <p className="text-sm text-gray-500">{isZh ? '演讲技巧与内容' : 'Speech skills and content'}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 flex items-center gap-4 border-l-4 border-purple-500 cursor-pointer hover:shadow-xl transition-all"
             onClick={() => setPage('dialogue')}>
          <div className="text-3xl font-bold text-purple-600">3</div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-800">{isZh ? '每日对话' : 'Daily Dialogue'}</h3>
            <p className="text-sm text-gray-500">{isZh ? '情景对话练习' : 'Situation dialogue practice'}</p>
          </div>
        </div>

        <div className="bg-gray-100 rounded-xl p-6 flex items-center gap-4 mt-8 cursor-pointer hover:bg-gray-200 transition-colors"
             onClick={() => setPage('home')}>
          <div className="text-3xl font-bold text-gray-400">4</div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-600">{isZh ? '返回主菜单' : 'Back to Home'}</h3>
          </div>
        </div>
      </div>

      <p className="mt-12 text-gray-500">
        {isZh ? '当前级别：' : 'Current Level: '}
        <span className="font-semibold">
          {preferences.learningLevel === 'beginner' ? (isZh ? '初级' : 'Beginner') :
           preferences.learningLevel === 'intermediate' ? (isZh ? '中级' : 'Intermediate') :
           (isZh ? '高级' : 'Advanced')}
        </span>
      </p>
    </div>
  )
}