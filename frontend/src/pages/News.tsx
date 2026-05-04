import { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useTTS } from '../hooks/useTTS'
import { fetchNews } from '../services/api'
import type { NewsItem } from '../services/api'
import { isTTSActivated } from '../hooks/useTTS'

export function News() {
  const { newsItems, currentNewsIndex, setNewsItems, setCurrentNewsIndex, preferences } = useAppStore()
  const { speak } = useTTS()
  const [showDetail, setShowDetail] = useState(false)
  const [loading, setLoading] = useState(false)

  // 加载新闻
  useEffect(() => {
    const loadNews = async () => {
      if (newsItems.length === 0) {
        setLoading(true)
        try {
          const data = await fetchNews(preferences.newsCategories)
          setNewsItems(data)
        } catch (error) {
          // Fallback to mock data if API fails
          const mockNews: NewsItem[] = [
            {
              id: '1',
              title: 'AI技术突破：新一代语言模型发布',
              summary: '科技公司发布新一代AI语言模型，性能提升显著。',
              detail: '该模型在多项基准测试中表现出色，推理能力大幅提升。',
              source: '科技日报',
              category: 'tech',
            },
            {
              id: '2',
              title: '研究发现：适当休息有益眼健康',
              summary: '医学研究表明，定期休息可有效缓解眼部疲劳。',
              detail: '专家建议每工作45分钟休息5分钟，闭眼放松或远眺。',
              source: '健康时报',
              category: 'health',
            },
            {
              id: '3',
              title: '智能穿戴设备市场持续增长',
              summary: '全球智能穿戴设备出货量同比增长25%。',
              detail: '智能眼镜、健康手环等产品受到消费者青睐。',
              source: '财经周刊',
              category: 'tech',
            },
          ]
          setNewsItems(mockNews)
        } finally {
          setLoading(false)
        }
      }
    }
    loadNews()
  }, [])

  // 播报当前新闻
  const speakCurrentNews = () => {
    if (newsItems.length > 0 && isTTSActivated()) {
      const item = newsItems[currentNewsIndex]
      const text = showDetail
        ? `${item.title}。${item.detail}`
        : `${item.title}。${item.summary}`
      speak(text)
    }
  }

  // 当新闻索引或详情状态改变时播报
  useEffect(() => {
    speakCurrentNews()
  }, [currentNewsIndex, showDetail, newsItems])

  // 键盘控制
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (newsItems.length === 0) return
      const key = e.key
      if (key === '1') {
        // 下一条
        setCurrentNewsIndex((currentNewsIndex + 1) % newsItems.length)
        setShowDetail(false)
      } else if (key === '2') {
        // 详情
        setShowDetail(true)
      } else if (key === '3') {
        // 重复播报
        speakCurrentNews()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [currentNewsIndex, newsItems, setCurrentNewsIndex, showDetail])

  const currentNews = newsItems[currentNewsIndex]
  const isZh = preferences.language === 'zh'

  if (loading || !currentNews) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="text-xl text-gray-600">{isZh ? '加载中...' : 'Loading...'}</div>
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 pb-32">
      <div className="flex-1 p-8">
        <div className="max-w-lg mx-auto">
          <div className="text-center mb-6">
            <span className="text-sm text-gray-500">
              {isZh ? '第' : ''} {currentNewsIndex + 1} / {newsItems.length} {isZh ? '条' : ''} · {currentNews.source}
            </span>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">{currentNews.title}</h2>
            <p className="text-gray-600 text-lg leading-relaxed mb-4">
              {showDetail ? currentNews.detail : currentNews.summary}
            </p>
            {showDetail && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-600">{isZh ? '正在播放详细内容' : 'Playing detailed content'}</p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => {
                setCurrentNewsIndex((currentNewsIndex + 1) % newsItems.length)
                setShowDetail(false)
              }}
              className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              {isZh ? '下一条' : 'Next'}
            </button>
            <button
              onClick={() => setShowDetail(true)}
              className={`p-3 rounded-lg transition-colors ${showDetail ? 'bg-green-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '详情' : 'Detail'}
            </button>
            <button
              onClick={speakCurrentNews}
              className="p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              🔊
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}