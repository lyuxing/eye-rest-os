import { useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS } from '../hooks/useTTS'

const categories = [
  { id: 'tech', label: '科技', labelEn: 'Tech' },
  { id: 'finance', label: '财经', labelEn: 'Finance' },
  { id: 'health', label: '健康', labelEn: 'Health' },
  { id: 'entertainment', label: '娱乐', labelEn: 'Entertainment' },
]

const languages = [
  { id: 'en', label: '英语', labelEn: 'English' },
  { id: 'ja', label: '日语', labelEn: 'Japanese' },
  { id: 'fr', label: '法语', labelEn: 'French' },
  { id: 'de', label: '德语', labelEn: 'German' },
  { id: 'es', label: '西班牙语', labelEn: 'Spanish' },
]

const levels = [
  { id: 'beginner', label: '初级', labelEn: 'Beginner', desc: '适合初学者', descEn: 'For beginners' },
  { id: 'intermediate', label: '中级', labelEn: 'Intermediate', desc: '有一定基础', descEn: 'Some experience' },
  { id: 'advanced', label: '高级', labelEn: 'Advanced', desc: '高阶学习', descEn: 'Advanced level' },
]

export function Settings() {
  const { preferences, setPreferences } = useAppStore()
  const { speak } = useTTS()
  const [activeSection, setActiveSection] = useState<string | null>(null)

  const isZh = preferences.language === 'zh'

  const handleLanguageChange = (lang: 'zh' | 'en') => {
    setPreferences({ language: lang })
    speak(lang === 'zh' ? '已切换为中文' : 'Switched to English')
  }

  const handleCategoryToggle = (categoryId: string) => {
    const newCategories = preferences.newsCategories.includes(categoryId)
      ? preferences.newsCategories.filter(c => c !== categoryId)
      : [...preferences.newsCategories, categoryId]
    setPreferences({ newsCategories: newCategories })
  }

  const handleRateChange = (rate: number) => {
    setPreferences({ speechRate: rate })
  }

  const handleLevelChange = (level: string) => {
    setPreferences({ learningLevel: level as 'beginner' | 'intermediate' | 'advanced' })
    speak(isZh ? `已切换到${levels.find(l => l.id === level)?.label}级别` : `Switched to ${level} level`)
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 pb-32">
      <div className="flex-1 p-8">
        <div className="max-w-lg mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
            {isZh ? '偏好设置' : 'Settings'}
          </h2>

          {/* Interface Language */}
          <div className="bg-white rounded-xl shadow p-6 mb-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700 font-medium">{isZh ? '界面语言' : 'Interface Language'}</span>
              <button
                onClick={() => setActiveSection(activeSection === 'language' ? null : 'language')}
                className="text-blue-500"
              >
                {preferences.language === 'zh' ? '中文' : 'English'}
              </button>
            </div>
            {activeSection === 'language' && (
              <div className="flex gap-3">
                <button
                  onClick={() => handleLanguageChange('zh')}
                  className={`flex-1 py-2 rounded-lg transition-colors ${preferences.language === 'zh' ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
                >
                  中文
                </button>
                <button
                  onClick={() => handleLanguageChange('en')}
                  className={`flex-1 py-2 rounded-lg transition-colors ${preferences.language === 'en' ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
                >
                  English
                </button>
              </div>
            )}
          </div>

          {/* News Categories */}
          <div className="bg-white rounded-xl shadow p-6 mb-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700 font-medium">{isZh ? '时讯类别' : 'News Categories'}</span>
              <span className="text-gray-400 text-sm">
                {preferences.newsCategories.length} {isZh ? '项已选' : 'selected'}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {categories.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => handleCategoryToggle(cat.id)}
                  className={`px-4 py-2 rounded-full transition-colors ${
                    preferences.newsCategories.includes(cat.id)
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {isZh ? cat.label : cat.labelEn}
                </button>
              ))}
            </div>
          </div>

          {/* Speech Rate */}
          <div className="bg-white rounded-xl shadow p-6 mb-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700 font-medium">{isZh ? '播报语速' : 'Speech Rate'}</span>
              <span className="text-gray-500">{preferences.speechRate.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={preferences.speechRate}
              onChange={(e) => handleRateChange(parseFloat(e.target.value))}
              className="w-full accent-blue-500"
            />
            <div className="flex justify-between text-sm text-gray-400 mt-2">
              <span>{isZh ? '慢' : 'Slow'}</span>
              <span>{isZh ? '快' : 'Fast'}</span>
            </div>
          </div>

          {/* Learning Language */}
          <div className="bg-white rounded-xl shadow p-6 mb-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700 font-medium">{isZh ? '学习语言' : 'Learning Language'}</span>
              <span className="text-gray-500">
                {languages.find(l => l.id === preferences.phraseLanguage)?.label || 'English'}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {languages.map(lang => (
                <button
                  key={lang.id}
                  onClick={() => setPreferences({ phraseLanguage: lang.id })}
                  className={`px-4 py-2 rounded-full transition-colors ${
                    preferences.phraseLanguage === lang.id
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {isZh ? lang.label : lang.labelEn}
                </button>
              ))}
            </div>
          </div>

          {/* Learning Level */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700 font-medium">{isZh ? '学习级别' : 'Learning Level'}</span>
              <span className="text-gray-500">
                {levels.find(l => l.id === preferences.learningLevel)?.label || '中级'}
              </span>
            </div>
            <div className="space-y-2">
              {levels.map(level => (
                <button
                  key={level.id}
                  onClick={() => handleLevelChange(level.id)}
                  className={`w-full p-3 rounded-lg text-left transition-colors ${
                    preferences.learningLevel === level.id
                      ? 'bg-purple-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <div className="font-medium">{isZh ? level.label : level.labelEn}</div>
                  <div className={`text-sm ${preferences.learningLevel === level.id ? 'text-purple-100' : 'text-gray-400'}`}>
                    {isZh ? level.desc : level.descEn}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}