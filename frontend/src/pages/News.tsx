import { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { useAuthStore } from '../store/useAuthStore'
import { useTTS } from '../hooks/useTTS'
import { fetchPersonalizedNews, recordAction, markNewsRead, markNewsSkipped } from '../services/api'
import type { NewsItem } from '../services/api'
import { isTTSActivated } from '../hooks/useTTS'

export function News() {
  const { newsItems, currentNewsIndex, setNewsItems, setCurrentNewsIndex, preferences } = useAppStore()
  const { token } = useAuthStore()
  const { speak } = useTTS()
  const [showDetail, setShowDetail] = useState(false)
  const [loading, setLoading] = useState(false)

  // 加载个性化新闻
  useEffect(() => {
    const loadNews = async () => {
      if (newsItems.length === 0) {
        setLoading(true)
        try {
          if (token) {
            // 使用推荐API获取个性化新闻
            const data = await fetchPersonalizedNews(token, 10)
            setNewsItems(data)
          } else {
            // 未登录时使用默认新闻
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
            ]
            setNewsItems(mockNews)
          }
        } catch (error) {
          console.error('Failed to load news:', error)
          setNewsItems([])
        } finally {
          setLoading(false)
        }
      }
    }
    loadNews()
  }, [token])

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

  // 处理下一条新闻
  const handleNext = async () => {
    if (newsItems.length === 0) return

    const currentNews = newsItems[currentNewsIndex]

    // 记录跳过行为
    if (token && currentNews) {
      try {
        await markNewsSkipped(token, currentNews.id)
      } catch (e) {
        console.error('Failed to record skip:', e)
      }
    }

    setCurrentNewsIndex((currentNewsIndex + 1) % newsItems.length)
    setShowDetail(false)
  }

  // 处理查看详情
  const handleDetail = async () => {
    if (newsItems.length === 0) return

    const currentNews = newsItems[currentNewsIndex]

    // 记录详情行为
    if (token && currentNews && !showDetail) {
      try {
        await recordAction(token, 'detail', 'news', currentNews.id, currentNews.category)
      } catch (e) {
        console.error('Failed to record detail:', e)
      }
    }

    setShowDetail(true)
  }

  // 处理新闻已读
  const handleMarkRead = async () => {
    if (newsItems.length === 0) return

    const currentNews = newsItems[currentNewsIndex]

    if (token && currentNews) {
      try {
        await markNewsRead(token, currentNews.id)
      } catch (e) {
        console.error('Failed to mark read:', e)
      }
    }
  }

  // 键盘控制
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (newsItems.length === 0) return
      const key = e.key
      if (key === '1') {
        handleNext()
      } else if (key === '2') {
        handleDetail()
      } else if (key === '3') {
        speakCurrentNews()
      } else if (key === '4') {
        handleMarkRead()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [currentNewsIndex, newsItems, showDetail])

  const currentNews = newsItems[currentNewsIndex]
  const isZh = preferences.language === 'zh'

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="text-xl text-gray-600">{isZh ? '正在获取个性化新闻...' : 'Loading personalized news...'}</div>
      </div>
    )
  }

  if (!currentNews) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="text-xl text-gray-600 mb-4">{isZh ? '暂无新闻' : 'No news available'}</div>
        <button
          onClick={async () => {
            setLoading(true)
            setNewsItems([])
            setCurrentNewsIndex(0)
            try {
              if (token) {
                const data = await fetchPersonalizedNews(token, 10)
                setNewsItems(data)
              }
            } catch (e) {
              console.error(e)
            } finally {
              setLoading(false)
            }
          }}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          {isZh ? '刷新' : 'Refresh'}
        </button>
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
            <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-600 rounded text-xs">
              {currentNews.category}
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

          <div className="grid grid-cols-4 gap-2">
            <button
              onClick={handleNext}
              className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
            >
              {isZh ? '下一条' : 'Next'}
            </button>
            <button
              onClick={handleDetail}
              className={`p-3 rounded-lg transition-colors text-sm ${showDetail ? 'bg-green-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              {isZh ? '详情' : 'Detail'}
            </button>
            <button
              onClick={speakCurrentNews}
              className="p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              🔊
            </button>
            <button
              onClick={handleMarkRead}
              className="p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors text-sm"
            >
              {isZh ? '已读' : 'Read'}
            </button>
          </div>

          <div className="mt-6 bg-gray-100 rounded-lg p-4 text-center">
            <p className="text-sm text-gray-500">
              {isZh ? '新闻根据你的兴趣个性化推荐' : 'News personalized based on your interests'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}