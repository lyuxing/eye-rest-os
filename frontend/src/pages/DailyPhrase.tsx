import { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS, isTTSActivated } from '../hooks/useTTS'
import { fetchDailyPhrase } from '../services/api'
import type { PhraseItem } from '../services/api'

const mockPhrase: PhraseItem = {
  id: '1',
  sentence: 'The early bird catches the worm.',
  pronunciation: '/ði ˈɜːrli bɜːrd ˈkætʃɪz ðə wɜːrm/',
  meaning: '早起的鸟儿有虫吃。（意指勤奋的人会获得成功）',
  example: "Remember, the early bird catches the worm, so let's start early tomorrow.",
  language: 'en',
  level: 'intermediate'
}

export function DailyPhrase() {
  const { dailyPhrase, setDailyPhrase, preferences, setPage } = useAppStore()
  const { speak } = useTTS()
  const [mode, setMode] = useState<'sentence' | 'meaning' | 'example'>('sentence')

  useEffect(() => {
    const loadPhrase = async () => {
      if (!dailyPhrase) {
        try {
          const data = await fetchDailyPhrase(preferences.phraseLanguage, preferences.learningLevel)
          setDailyPhrase(data)
        } catch {
          setDailyPhrase(mockPhrase)
        }
      }
    }
    loadPhrase()
  }, [])

  // 播报当前内容
  const speakCurrent = (m: 'sentence' | 'meaning' | 'example') => {
    if (!dailyPhrase || !isTTSActivated()) return
    const text = m === 'sentence'
      ? dailyPhrase.sentence
      : m === 'meaning'
      ? dailyPhrase.meaning
      : dailyPhrase.example
    speak(text)
  }

  useEffect(() => {
    speakCurrent(mode)
  }, [mode, dailyPhrase])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (!dailyPhrase) return
      const key = e.key
      if (key === '1') {
        setMode('sentence')
        speakCurrent('sentence')
      } else if (key === '2') {
        setMode('meaning')
        speakCurrent('meaning')
      } else if (key === '3') {
        setMode('example')
        speakCurrent('example')
      } else if (key === '4') {
        setPage('learning')
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [dailyPhrase, setPage])

  const phrase = dailyPhrase || mockPhrase
  const isZh = preferences.language === 'zh'

  const languageLabels: Record<string, string> = {
    en: isZh ? '英语' : 'English',
    ja: isZh ? '日语' : 'Japanese',
    fr: isZh ? '法语' : 'French',
    de: isZh ? '德语' : 'German',
    es: isZh ? '西班牙语' : 'Spanish'
  }

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-green-50 to-white pb-32">
      <div className="flex-1 p-8">
        <div className="max-w-lg mx-auto">
          <div className="text-center mb-6">
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
              {isZh ? '每日一句' : 'Daily Phrase'} · {languageLabels[phrase.language] || phrase.language}
            </span>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
            <p className="text-2xl font-semibold text-gray-800 mb-4 text-center cursor-pointer hover:text-green-600"
               onClick={() => speakCurrent('sentence')}>
              {phrase.sentence}
            </p>
            <p className="text-gray-500 text-center mb-4 cursor-pointer hover:text-green-600"
               onClick={() => speakCurrent('sentence')}>
              {phrase.pronunciation}
            </p>
            <div className="border-t pt-4 cursor-pointer hover:text-green-600"
                 onClick={() => speakCurrent('meaning')}>
              <p className="text-gray-600 text-center">{phrase.meaning}</p>
            </div>
          </div>

          {mode === 'example' && (
            <div className="bg-blue-50 rounded-xl p-4 mb-4">
              <div className="text-sm text-blue-600 mb-2">{isZh ? '例句：' : 'Example:'}</div>
              <p className="text-gray-700 cursor-pointer hover:text-blue-600"
                 onClick={() => speakCurrent('example')}>{phrase.example}</p>
            </div>
          )}

          <div className="grid grid-cols-3 gap-3 text-center">
            <button
              onClick={() => { setMode('sentence'); speakCurrent('sentence') }}
              className={`p-3 rounded-lg transition-colors ${mode === 'sentence' ? 'bg-green-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '原句' : 'Sentence'}
            </button>
            <button
              onClick={() => { setMode('meaning'); speakCurrent('meaning') }}
              className={`p-3 rounded-lg transition-colors ${mode === 'meaning' ? 'bg-green-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '释义' : 'Meaning'}
            </button>
            <button
              onClick={() => { setMode('example'); speakCurrent('example') }}
              className={`p-3 rounded-lg transition-colors ${mode === 'example' ? 'bg-green-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '例句' : 'Example'}
            </button>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={() => speakCurrent(mode)}
              className="px-6 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
            >
              🔊 {isZh ? '重新播放' : 'Replay'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}