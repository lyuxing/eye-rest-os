import { useCallback, useEffect } from 'react'
import { useAppStore } from '../store/useAppStore'

interface NavOption {
  label: string
  action: () => void
}

export function useNavigation() {
  const { currentPage, setPage, preferences } = useAppStore()

  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    const key = event.key
    if (!['1', '2', '3', '4'].includes(key)) return

    const keyNum = parseInt(key)

    // Handle navigation based on current page
    switch (currentPage) {
      case 'home':
        if (keyNum === 1) setPage('news')
        else if (keyNum === 2) setPage('learning')
        else if (keyNum === 3) setPage('game')
        else if (keyNum === 4) setPage('settings')
        break
      case 'learning':
        // Learning submenu handled by Learning page
        break
      case 'game':
        // Game selection handled by Game page
        break
      default:
        if (keyNum === 4) setPage('home')
    }
  }, [currentPage, setPage])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [handleKeyPress])

  const getNavOptions = useCallback((): NavOption[] => {
    const isZh = preferences.language === 'zh'

    switch (currentPage) {
      case 'home':
        return [
          { label: isZh ? '时讯简报' : 'News', action: () => setPage('news') },
          { label: isZh ? '语言学习' : 'Learning', action: () => setPage('learning') },
          { label: isZh ? '音频游戏' : 'Game', action: () => setPage('game') },
          { label: isZh ? '偏好设置' : 'Settings', action: () => setPage('settings') },
        ]
      case 'news':
        return [
          { label: isZh ? '下一条' : 'Next', action: () => {} },
          { label: isZh ? '详情' : 'Detail', action: () => {} },
          { label: isZh ? '收藏' : 'Save', action: () => {} },
          { label: isZh ? '返回' : 'Back', action: () => setPage('home') },
        ]
      case 'phrase':
        return [
          { label: isZh ? '原句' : 'Sentence', action: () => {} },
          { label: isZh ? '释义' : 'Meaning', action: () => {} },
          { label: isZh ? '例句' : 'Example', action: () => {} },
          { label: isZh ? '返回' : 'Back', action: () => setPage('learning') },
        ]
      case 'speech':
        return [
          { label: isZh ? '播放' : 'Play', action: () => {} },
          { label: isZh ? '重点' : 'Key Points', action: () => {} },
          { label: isZh ? '词汇' : 'Vocab', action: () => {} },
          { label: isZh ? '返回' : 'Back', action: () => setPage('learning') },
        ]
      case 'dialogue':
        return [
          { label: isZh ? '播放' : 'Play', action: () => {} },
          { label: isZh ? '词汇' : 'Vocab', action: () => {} },
          { label: isZh ? '文化' : 'Culture', action: () => {} },
          { label: isZh ? '返回' : 'Back', action: () => setPage('learning') },
        ]
      case 'game':
        return [
          { label: '1', action: () => {} },
          { label: '2', action: () => {} },
          { label: '3', action: () => {} },
          { label: isZh ? '返回' : 'Back', action: () => setPage('home') },
        ]
      case 'settings':
        return [
          { label: isZh ? '语言' : 'Language', action: () => {} },
          { label: isZh ? '类别' : 'Category', action: () => {} },
          { label: isZh ? '语速' : 'Speed', action: () => {} },
          { label: isZh ? '返回' : 'Back', action: () => setPage('home') },
        ]
      case 'learning':
        return [
          { label: isZh ? '每日一句' : 'Phrase', action: () => setPage('phrase') },
          { label: isZh ? '每日演讲' : 'Speech', action: () => setPage('speech') },
          { label: isZh ? '每日对话' : 'Dialogue', action: () => setPage('dialogue') },
          { label: isZh ? '返回' : 'Back', action: () => setPage('home') },
        ]
      default:
        return [
          { label: '1', action: () => {} },
          { label: '2', action: () => {} },
          { label: '3', action: () => {} },
          { label: isZh ? '返回' : 'Back', action: () => setPage('home') },
        ]
    }
  }, [currentPage, setPage, preferences.language])

  return { currentPage, getNavOptions, setPage }
}