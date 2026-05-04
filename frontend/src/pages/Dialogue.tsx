import { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS, isTTSActivated } from '../hooks/useTTS'
import { fetchDailyDialogue } from '../services/api'
import type { DialogueItem } from '../services/api'

const mockDialogue: DialogueItem = {
  id: '1',
  situation: 'Restaurant Ordering',
  dialogue: [
    { speaker: 'A', text: 'Good evening! Are you ready to order?' },
    { speaker: 'B', text: "Yes, I'd like the grilled salmon, please." },
    { speaker: 'A', text: 'Would you like any sides with that?' },
    { speaker: 'B', text: "I'll have the roasted vegetables." }
  ],
  vocabulary: ['grilled', 'sides', 'roasted'],
  cultural_notes: '在西方餐厅，通常先点主菜，再点配菜和饮品',
  language: 'en',
  level: 'intermediate'
}

export function Dialogue() {
  const { dailyDialogue, setDailyDialogue, preferences } = useAppStore()
  const { speak } = useTTS()
  const [currentLine, setCurrentLine] = useState(0)
  const [showVocab, setShowVocab] = useState(false)
  const [showCulture, setShowCulture] = useState(false)

  useEffect(() => {
    const loadDialogue = async () => {
      if (!dailyDialogue) {
        try {
          const data = await fetchDailyDialogue(preferences.phraseLanguage, preferences.learningLevel)
          setDailyDialogue(data)
        } catch {
          setDailyDialogue(mockDialogue)
        }
      }
    }
    loadDialogue()
  }, [])

  const speakLine = (idx: number) => {
    if (!dailyDialogue || !isTTSActivated()) return
    const line = dailyDialogue.dialogue[idx]
    speak(`${line.speaker}: ${line.text}`)
  }

  useEffect(() => {
    if (dailyDialogue && dailyDialogue.dialogue.length > 0 && isTTSActivated()) {
      speakLine(currentLine)
    }
  }, [currentLine, dailyDialogue])

  const nextLine = () => {
    if (!dailyDialogue) return
    setCurrentLine((prev) => (prev + 1) % dailyDialogue.dialogue.length)
    setShowVocab(false)
    setShowCulture(false)
  }

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (!dailyDialogue) return
      const key = e.key

      if (key === '1') {
        nextLine()
      } else if (key === '2') {
        setShowVocab(true)
        setShowCulture(false)
        speak(dailyDialogue.vocabulary.join(', '))
      } else if (key === '3') {
        setShowVocab(false)
        setShowCulture(true)
        if (dailyDialogue.cultural_notes) {
          speak(dailyDialogue.cultural_notes)
        }
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [dailyDialogue])

  const dialogue = dailyDialogue || mockDialogue
  const isZh = preferences.language === 'zh'

  const levelLabels: Record<string, string> = {
    beginner: isZh ? '初级' : 'Beginner',
    intermediate: isZh ? '中级' : 'Intermediate',
    advanced: isZh ? '高级' : 'Advanced'
  }

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-purple-50 to-white pb-32">
      <div className="flex-1 p-8">
        <div className="max-w-lg mx-auto">
          <div className="text-center mb-6">
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
              {isZh ? '每日对话' : 'Daily Dialogue'} · {levelLabels[dialogue.level] || dialogue.level}
            </span>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-4 mb-6">
            <div className="text-center text-gray-500 mb-4 text-sm">
              {isZh ? '场景：' : 'Situation: '}{dialogue.situation}
            </div>

            <div className="space-y-3">
              {dialogue.dialogue.map((line, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg transition-all cursor-pointer ${
                    idx === currentLine
                      ? 'bg-purple-100 border-l-4 border-purple-500'
                      : line.speaker === 'A'
                      ? 'bg-gray-50 hover:bg-gray-100'
                      : 'bg-blue-50 hover:bg-blue-100'
                  }`}
                  onClick={() => { setCurrentLine(idx); speakLine(idx) }}
                >
                  <span className={`font-bold ${line.speaker === 'A' ? 'text-purple-600' : 'text-blue-600'}`}>
                    {line.speaker}:
                  </span>
                  <span className="ml-2 text-gray-700">{line.text}</span>
                </div>
              ))}
            </div>
          </div>

          {showVocab && (
            <div className="bg-green-50 rounded-xl p-4 mb-4">
              <h3 className="font-semibold text-green-700 mb-2">{isZh ? '词汇：' : 'Vocabulary:'}</h3>
              <div className="flex flex-wrap gap-2">
                {dialogue.vocabulary.map((word, idx) => (
                  <span key={idx}
                        className="px-3 py-1 bg-white rounded-full text-gray-700 shadow-sm cursor-pointer hover:text-green-600"
                        onClick={() => speak(word)}>
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {showCulture && dialogue.cultural_notes && (
            <div className="bg-yellow-50 rounded-xl p-4 mb-4">
              <h3 className="font-semibold text-yellow-700 mb-2">{isZh ? '文化提示：' : 'Cultural Notes:'}</h3>
              <p className="text-gray-700">{dialogue.cultural_notes}</p>
            </div>
          )}

          <div className="grid grid-cols-3 gap-3 text-center">
            <button
              onClick={nextLine}
              className="p-3 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              {isZh ? '下一句' : 'Next'}
            </button>
            <button
              onClick={() => {
                setShowVocab(true)
                setShowCulture(false)
                speak(dialogue.vocabulary.join(', '))
              }}
              className={`p-3 rounded-lg transition-colors ${showVocab ? 'bg-purple-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '词汇' : 'Vocab'}
            </button>
            <button
              onClick={() => {
                setShowVocab(false)
                setShowCulture(true)
                if (dialogue.cultural_notes) speak(dialogue.cultural_notes)
              }}
              className={`p-3 rounded-lg transition-colors ${showCulture ? 'bg-purple-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '文化' : 'Culture'}
            </button>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={() => speakLine(currentLine)}
              className="px-6 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
            >
              🔊 {isZh ? '重新播放' : 'Replay'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}