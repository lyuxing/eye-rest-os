import { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS, isTTSActivated } from '../hooks/useTTS'
import { fetchDailySpeech } from '../services/api'
import type { SpeechItem } from '../services/api'

const mockSpeech: SpeechItem = {
  id: '1',
  title: 'The Value of Time',
  content: 'Time is our most precious resource. Unlike money, we cannot earn more time. Each day, we have exactly 24 hours to pursue our dreams, help others, and create memories.',
  key_points: ['时间的珍贵性', '时间与金钱的对比', '如何利用时间'],
  vocabulary: ['precious', 'resource', 'pursue'],
  language: 'en',
  level: 'intermediate'
}

export function Speech() {
  const { dailySpeech, setDailySpeech, preferences } = useAppStore()
  const { speak } = useTTS()
  const [mode, setMode] = useState<'content' | 'points' | 'vocab'>('content')

  useEffect(() => {
    const loadSpeech = async () => {
      if (!dailySpeech) {
        try {
          const data = await fetchDailySpeech(preferences.phraseLanguage, preferences.learningLevel)
          setDailySpeech(data)
        } catch {
          setDailySpeech(mockSpeech)
        }
      }
    }
    loadSpeech()
  }, [])

  const speakCurrent = (m: 'content' | 'points' | 'vocab') => {
    if (!dailySpeech || !isTTSActivated()) return
    const text = m === 'content'
      ? dailySpeech.content
      : m === 'points'
      ? dailySpeech.key_points.join('。')
      : dailySpeech.vocabulary.join(', ')
    speak(text)
  }

  useEffect(() => {
    speakCurrent(mode)
  }, [mode, dailySpeech])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (!dailySpeech) return
      const key = e.key
      if (key === '1') {
        setMode('content')
        speakCurrent('content')
      } else if (key === '2') {
        setMode('points')
        speakCurrent('points')
      } else if (key === '3') {
        setMode('vocab')
        speakCurrent('vocab')
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [dailySpeech])

  const speech = dailySpeech || mockSpeech
  const isZh = preferences.language === 'zh'

  const levelLabels: Record<string, string> = {
    beginner: isZh ? '初级' : 'Beginner',
    intermediate: isZh ? '中级' : 'Intermediate',
    advanced: isZh ? '高级' : 'Advanced'
  }

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-blue-50 to-white pb-32">
      <div className="flex-1 p-8">
        <div className="max-w-lg mx-auto">
          <div className="text-center mb-6">
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              {isZh ? '每日演讲' : 'Daily Speech'} · {levelLabels[speech.level] || speech.level}
            </span>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4 text-center cursor-pointer hover:text-blue-600"
                onClick={() => speakCurrent('content')}>
              {speech.title}
            </h2>
            <p className="text-gray-700 leading-relaxed text-lg cursor-pointer hover:text-blue-600"
               onClick={() => speakCurrent('content')}>
              {speech.content}
            </p>
          </div>

          {mode === 'points' && (
            <div className="bg-yellow-50 rounded-xl p-4 mb-4">
              <h3 className="font-semibold text-yellow-700 mb-2">{isZh ? '要点：' : 'Key Points:'}</h3>
              <ul className="space-y-2">
                {speech.key_points.map((point, idx) => (
                  <li key={idx} className="text-gray-700 cursor-pointer hover:text-yellow-600"
                      onClick={() => speak(point)}>• {point}</li>
                ))}
              </ul>
            </div>
          )}

          {mode === 'vocab' && (
            <div className="bg-green-50 rounded-xl p-4 mb-4">
              <h3 className="font-semibold text-green-700 mb-2">{isZh ? '词汇：' : 'Vocabulary:'}</h3>
              <div className="flex flex-wrap gap-2">
                {speech.vocabulary.map((word, idx) => (
                  <span key={idx}
                        className="px-3 py-1 bg-white rounded-full text-gray-700 shadow-sm cursor-pointer hover:text-green-600"
                        onClick={() => speak(word)}>
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-3 gap-3 text-center">
            <button
              onClick={() => { setMode('content'); speakCurrent('content') }}
              className={`p-3 rounded-lg transition-colors ${mode === 'content' ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '内容' : 'Content'}
            </button>
            <button
              onClick={() => { setMode('points'); speakCurrent('points') }}
              className={`p-3 rounded-lg transition-colors ${mode === 'points' ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '要点' : 'Points'}
            </button>
            <button
              onClick={() => { setMode('vocab'); speakCurrent('vocab') }}
              className={`p-3 rounded-lg transition-colors ${mode === 'vocab' ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '词汇' : 'Vocab'}
            </button>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={() => speakCurrent(mode)}
              className="px-6 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              🔊 {isZh ? '重新播放' : 'Replay'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}