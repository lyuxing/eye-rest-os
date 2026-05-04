import axios from 'axios'

const API_BASE = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface NewsItem {
  id: string
  title: string
  summary: string
  detail: string
  source: string
  category: string
}

export interface PhraseItem {
  id: string
  sentence: string
  pronunciation: string
  meaning: string
  example: string
  language: string
  level?: string
}

export interface SpeechItem {
  id: string
  title: string
  content: string
  key_points: string[]
  vocabulary: string[]
  language: string
  level: string
}

export interface DialogueItem {
  id: string
  situation: string
  dialogue: Array<{ speaker: string; text: string }>
  vocabulary: string[]
  cultural_notes?: string
  language: string
  level: string
}

export interface GameInfo {
  id: string
  title: string
  description: string
  difficulty: string
}

export interface GameSession {
  session_id: string
  game_id: string
  title?: string
  scene_id: string
  narration: string
  choices: Array<{ key: string; text: string; next: string }>
  is_end: boolean
  result?: string
}

export interface LevelInfo {
  id: string
  name: string
  description: string
}

export interface LanguageInfo {
  id: string
  name: string
}

// TTS API - 获取音频Blob URL（推荐方式）
export const getTTSAudioUrl = async (
  text: string,
  lang: string = 'zh',
  rate: number = 1.0,
  gender: string = 'female'
): Promise<string> => {
  try {
    // 构建完整的URL，确保参数正确编码
    const params = new URLSearchParams()
    params.append('text', text)
    params.append('lang', lang)
    params.append('rate', rate.toString())
    params.append('gender', gender)

    const url = `${API_BASE}/tts/generate/raw?${params.toString()}`
    console.log('TTS URL:', url.substring(0, 100) + '...')

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg'
      }
    })

    if (!response.ok) {
      throw new Error(`TTS request failed: ${response.status}`)
    }

    const blob = await response.blob()
    const blobUrl = URL.createObjectURL(blob)
    return blobUrl
  } catch (error) {
    console.error('TTS API error:', error)
    throw error
  }
}

// News APIs
export const fetchNews = async (categories?: string[]): Promise<NewsItem[]> => {
  const params = categories ? { categories } : {}
  const response = await api.get('/news/', { params })
  return response.data
}

export const summarizeNews = async (newsId: string, maxLength?: number): Promise<{ summary: string }> => {
  const response = await api.post(`/news/${newsId}/summarize`, null, {
    params: { max_length: maxLength || 100 }
  })
  return response.data
}

// Learning APIs
export const fetchDailyPhrase = async (language: string = 'en', level: string = 'intermediate'): Promise<PhraseItem> => {
  const response = await api.get('/phrase/daily', { params: { language, level } })
  return response.data
}

export const fetchDailySpeech = async (language: string = 'en', level: string = 'intermediate'): Promise<SpeechItem> => {
  const response = await api.get('/phrase/speech', { params: { language, level } })
  return response.data
}

export const fetchDailyDialogue = async (language: string = 'en', level: string = 'intermediate'): Promise<DialogueItem> => {
  const response = await api.get('/phrase/dialogue', { params: { language, level } })
  return response.data
}

export const fetchLevels = async (): Promise<LevelInfo[]> => {
  const response = await api.get('/phrase/levels/list')
  return response.data
}

export const fetchLanguages = async (): Promise<LanguageInfo[]> => {
  const response = await api.get('/phrase/languages/list')
  return response.data
}

// Game APIs
export const fetchGameList = async (): Promise<GameInfo[]> => {
  const response = await api.get('/game/list')
  return response.data
}

export const startGame = async (gameId: string): Promise<GameSession> => {
  const response = await api.post(`/game/${gameId}/start`)
  return response.data
}

export const makeGameChoice = async (sessionId: string, choice: string): Promise<GameSession> => {
  const response = await api.post('/game/choice', { session_id: sessionId, choice })
  return response.data
}

export const getGameSession = async (sessionId: string): Promise<GameSession> => {
  const response = await api.get(`/game/session/${sessionId}`)
  return response.data
}

export const endGameSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/game/session/${sessionId}`)
}

// Preferences APIs
export const fetchPreferences = async (userId: string) => {
  const response = await api.get(`/preferences/${userId}`)
  return response.data
}

export const updatePreferences = async (data: {
  user_id: string
  language: string
  news_categories: string[]
  speech_rate: number
  phrase_language: string
}) => {
  const response = await api.post('/preferences/', data)
  return response.data
}