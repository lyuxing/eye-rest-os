import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import { useAppStore } from '../store/useAppStore'
import { useTTS } from '../hooks/useTTS'

const availableCategories = [
  { id: 'tech', label: '科技', labelEn: 'Tech', icon: '💻' },
  { id: 'finance', label: '财经', labelEn: 'Finance', icon: '📈' },
  { id: 'health', label: '健康', labelEn: 'Health', icon: '🏥' },
  { id: 'entertainment', label: '娱乐', labelEn: 'Entertainment', icon: '🎬' },
  { id: 'science', label: '科学', labelEn: 'Science', icon: '🔬' },
  { id: 'sports', label: '体育', labelEn: 'Sports', icon: '⚽' },
]

const suggestedKeywords: Record<string, string[]> = {
  'tech': ['人工智能', '区块链', '云计算', '新能源', '智能手机'],
  'finance': ['股票', '基金', '投资', '理财', '加密货币'],
  'health': ['养生', '健身', '营养', '心理健康', '睡眠'],
  'entertainment': ['电影', '音乐', '游戏', '综艺', '明星'],
  'science': ['太空探索', '生物技术', '环保', '物理', '化学'],
  'sports': ['足球', '篮球', '网球', '奥运会', '电竞'],
}

export function Onboarding() {
  const [step, setStep] = useState(1)
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [customKeywords, setCustomKeywords] = useState<string[]>([])
  const [newKeyword, setNewKeyword] = useState('')
  const [saving, setSaving] = useState(false)

  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { setPreferences } = useAppStore()
  const { speak } = useTTS()

  const handleCategoryToggle = (categoryId: string) => {
    const newCategories = selectedCategories.includes(categoryId)
      ? selectedCategories.filter(c => c !== categoryId)
      : [...selectedCategories, categoryId]
    setSelectedCategories(newCategories)

    // 添加推荐关键词
    if (!selectedCategories.includes(categoryId) && suggestedKeywords[categoryId]) {
      const newKeywords = [...customKeywords]
      suggestedKeywords[categoryId].forEach(kw => {
        if (!newKeywords.includes(kw)) {
          newKeywords.push(kw)
        }
      })
      setCustomKeywords(newKeywords)
    }
  }

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !customKeywords.includes(newKeyword.trim())) {
      setCustomKeywords([...customKeywords, newKeyword.trim()])
      setNewKeyword('')
    }
  }

  const handleRemoveKeyword = (keyword: string) => {
    setCustomKeywords(customKeywords.filter(k => k !== keyword))
  }

  const handleComplete = async () => {
    setSaving(true)

    try {
      // 保存偏好设置到后端
      const token = useAuthStore.getState().token
      const response = await fetch('http://localhost:8000/onboarding/interests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          categories: selectedCategories,
          keywords: customKeywords,
          language: 'zh',
          phrase_language: 'en',
          learning_level: 'intermediate'
        })
      })

      if (response.ok) {
        // 更新本地状态
        setPreferences({
          newsCategories: selectedCategories,
          phraseLanguage: 'en',
          learningLevel: 'intermediate'
        })

        // 更新用户状态，标记onboarding完成
        useAuthStore.getState().setUser({
          ...useAuthStore.getState().user!,
          onboarding_completed: true
        })

        speak('设置完成，欢迎来到 Eye Rest OS')
        navigate('/home')
      } else {
        throw new Error('保存失败')
      }
    } catch (error) {
      console.error('Onboarding error:', error)
      speak('保存失败，请重试')
    } finally {
      setSaving(false)
    }
  }

  const handleSkip = () => {
    speak('跳过设置')
    navigate('/home')
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white flex flex-col">
      <div className="flex-1 p-8">
        <div className="max-w-lg mx-auto">
          {/* 进度指示器 */}
          <div className="flex items-center justify-center mb-8">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                    step >= s
                      ? 'bg-purple-500 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {s}
                </div>
                {s < 3 && (
                  <div
                    className={`w-12 h-1 mx-1 ${
                      step > s ? 'bg-purple-500' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Step 1: 欢迎 */}
          {step === 1 && (
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-800 mb-4">
                欢迎来到 Eye Rest OS
              </h1>
              <p className="text-gray-600 mb-8">
                {user?.display_name || '用户'}，让我们为你定制个性化的内容体验
              </p>
              <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
                <p className="text-gray-500 mb-4">
                  我们需要了解你的兴趣偏好，以便为你推荐最合适的内容。
                </p>
                <ul className="text-left text-gray-600 space-y-2">
                  <li>• 选择你感兴趣的领域</li>
                  <li>• 添加特定的关键词</li>
                  <li>• 完成后即可开始使用</li>
                </ul>
              </div>
              <button
                onClick={() => {
                  speak('选择你感兴趣的领域')
                  setStep(2)
                }}
                className="px-8 py-3 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 transition-colors"
              >
                开始设置
              </button>
            </div>
          )}

          {/* Step 2: 选择类别 */}
          {step === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2 text-center">
                选择感兴趣的领域
              </h2>
              <p className="text-gray-500 text-center mb-6">
                至少选择一个类别
              </p>

              <div className="grid grid-cols-2 gap-4 mb-8">
                {availableCategories.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => handleCategoryToggle(cat.id)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      selectedCategories.includes(cat.id)
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <div className="text-3xl mb-2">{cat.icon}</div>
                    <div className="font-medium text-gray-800">{cat.label}</div>
                    <div className="text-sm text-gray-500">{cat.labelEn}</div>
                  </button>
                ))}
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50"
                >
                  上一步
                </button>
                <button
                  onClick={() => {
                    speak('添加你感兴趣的关键词')
                    setStep(3)
                  }}
                  disabled={selectedCategories.length === 0}
                  className="flex-1 py-3 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 disabled:opacity-50"
                >
                  下一步
                </button>
              </div>
            </div>
          )}

          {/* Step 3: 添加关键词 */}
          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2 text-center">
                添加感兴趣的关键词
              </h2>
              <p className="text-gray-500 text-center mb-6">
                这些关键词将用于精准推荐
              </p>

              <div className="bg-white rounded-xl shadow-lg p-4 mb-4">
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
                    placeholder="输入关键词..."
                    className="flex-1 px-4 py-2 border rounded-lg"
                  />
                  <button
                    onClick={handleAddKeyword}
                    className="px-4 py-2 bg-purple-500 text-white rounded-lg"
                  >
                    添加
                  </button>
                </div>

                <div className="flex flex-wrap gap-2">
                  {customKeywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full flex items-center gap-1"
                    >
                      {keyword}
                      <button
                        onClick={() => handleRemoveKeyword(keyword)}
                        className="text-purple-500 hover:text-purple-700"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="text-sm text-gray-500 mb-6">
                已选择类别: {selectedCategories.map(c =>
                  availableCategories.find(cat => cat.id === c)?.label
                ).join('、')}
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 py-3 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50"
                >
                  上一步
                </button>
                <button
                  onClick={handleSkip}
                  className="flex-1 py-3 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50"
                >
                  跳过
                </button>
                <button
                  onClick={handleComplete}
                  disabled={saving}
                  className="flex-1 py-3 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 disabled:opacity-50"
                >
                  {saving ? '保存中...' : '完成'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
