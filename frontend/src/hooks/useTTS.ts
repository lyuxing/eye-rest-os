import { useCallback, useRef, useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { getTTSAudioUrl } from '../services/api'

// 全局TTS状态
let ttsActivated = false

export function useTTS() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioQueue = useRef<string[]>([])
  const isPlayingRef = useRef(false)
  const currentBlobUrlRef = useRef<string | null>(null)  // 记录当前播放的blob URL
  const { preferences, setIsPlaying } = useAppStore()
  const [isReady, setIsReady] = useState(false)

  // 创建音频元素
  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio()
      audioRef.current.onended = () => {
        isPlayingRef.current = false
        setIsPlaying(false)
        // 清理当前的blob URL
        if (currentBlobUrlRef.current) {
          URL.revokeObjectURL(currentBlobUrlRef.current)
          currentBlobUrlRef.current = null
        }
        // 播放队列中的下一个
        playNextInQueue()
      }
      audioRef.current.onerror = (e) => {
        console.error('Audio error:', e)
        isPlayingRef.current = false
        setIsPlaying(false)
        // 清理blob URL
        if (currentBlobUrlRef.current) {
          URL.revokeObjectURL(currentBlobUrlRef.current)
          currentBlobUrlRef.current = null
        }
        playNextInQueue()
      }
    }
    setIsReady(true)
  }, [setIsPlaying])

  // 清理函数：停止当前播放并清空队列
  const cleanup = useCallback(() => {
    // 停止音频
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.src = ''
      audioRef.current.load()  // 强制重置
    }

    // 清理blob URL
    if (currentBlobUrlRef.current) {
      URL.revokeObjectURL(currentBlobUrlRef.current)
      currentBlobUrlRef.current = null
    }

    // 清空队列中的blob URLs
    audioQueue.current.forEach(url => URL.revokeObjectURL(url))
    audioQueue.current = []

    isPlayingRef.current = false
    setIsPlaying(false)
  }, [setIsPlaying])

  const playNextInQueue = useCallback(() => {
    if (audioQueue.current.length > 0) {
      const nextUrl = audioQueue.current.shift()
      if (nextUrl && audioRef.current) {
        currentBlobUrlRef.current = nextUrl
        playAudioUrl(nextUrl)
      }
    }
  }, [])

  const playAudioUrl = useCallback((url: string) => {
    if (!audioRef.current) return

    console.log('🔊 Playing audio')
    audioRef.current.src = url
    audioRef.current.load()  // 确保加载新音频
    audioRef.current.play().catch(e => {
      console.error('Play error:', e)
      isPlayingRef.current = false
      setIsPlaying(false)
    })
    isPlayingRef.current = true
    setIsPlaying(true)
  }, [setIsPlaying])

  const speak = useCallback(async (text: string, onEnd?: () => void) => {
    if (!text || !text.trim()) return

    // 先清理之前的播放（重要！）
    cleanup()

    // 判断语言
    const hasChinese = /[一-龥]/.test(text)
    const lang = hasChinese ? 'zh' : preferences.phraseLanguage || 'en'
    const rate = preferences.speechRate

    console.log('🔊 TTS request:', text.substring(0, 50) + '...', 'lang:', lang)

    try {
      // 使用后端TTS服务获取音频URL
      const audioUrl = await getTTSAudioUrl(text, lang, rate, 'female')

      // 直接播放
      currentBlobUrlRef.current = audioUrl
      playAudioUrl(audioUrl)

      // 设置结束回调
      if (onEnd && audioRef.current) {
        const originalOnended = audioRef.current.onended
        audioRef.current.onended = () => {
          isPlayingRef.current = false
          setIsPlaying(false)
          // 清理blob URL
          if (currentBlobUrlRef.current) {
            URL.revokeObjectURL(currentBlobUrlRef.current)
            currentBlobUrlRef.current = null
          }
          onEnd()
          playNextInQueue()
          // 恢复原来的onended
          if (audioRef.current) {
            audioRef.current.onended = originalOnended
          }
        }
      }
    } catch (error) {
      console.error('TTS error:', error)
      // 降级到Web Speech API
      fallbackToWebSpeech(text, rate, hasChinese, onEnd)
    }
  }, [preferences.speechRate, preferences.phraseLanguage, setIsPlaying, playAudioUrl, playNextInQueue, cleanup])

  const fallbackToWebSpeech = (text: string, rate: number, hasChinese: boolean, onEnd?: () => void) => {
    if (!('speechSynthesis' in window)) {
      console.warn('No TTS available')
      return
    }

    console.log('🔊 Falling back to Web Speech API')

    // 先停止之前的播放
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = hasChinese ? 'zh-CN' : 'en-US'
    utterance.rate = rate
    utterance.onend = () => {
      setIsPlaying(false)
      onEnd?.()
    }
    utterance.onerror = () => {
      setIsPlaying(false)
    }
    window.speechSynthesis.speak(utterance)
    setIsPlaying(true)
  }

  // 激活TTS（需要用户交互）
  const activateTTS = useCallback(() => {
    if (ttsActivated) return true
    ttsActivated = true
    console.log('🔊 TTS activated (Edge TTS mode)')
    return true
  }, [])

  const stop = useCallback(() => {
    cleanup()
    // 也停止Web Speech API
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }, [cleanup])

  const pause = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
    }
  }, [])

  const resume = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.play()
    }
  }, [])

  return {
    speak,
    stop,
    pause,
    resume,
    activateTTS,
    isReady,
    isActivated: ttsActivated
  }
}

// 导出检查函数
export function isTTSActivated() {
  return ttsActivated
}