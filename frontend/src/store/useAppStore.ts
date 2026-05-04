import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Page = 'home' | 'news' | 'phrase' | 'speech' | 'dialogue' | 'game' | 'settings' | 'learning'
export type LearningMode = 'phrase' | 'speech' | 'dialogue'
export type Level = 'beginner' | 'intermediate' | 'advanced'

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

export interface UserPreferences {
  language: 'zh' | 'en'
  newsCategories: string[]
  speechRate: number
  phraseLanguage: string
  learningLevel: Level
}

interface AppState {
  currentPage: Page
  preferences: UserPreferences
  newsItems: NewsItem[]
  currentNewsIndex: number
  dailyPhrase: PhraseItem | null
  dailySpeech: SpeechItem | null
  dailyDialogue: DialogueItem | null
  gameSession: GameSession | null
  isPlaying: boolean
  learningMode: LearningMode

  // Actions
  setPage: (page: Page) => void
  setPreferences: (prefs: Partial<UserPreferences>) => void
  setNewsItems: (items: NewsItem[]) => void
  setCurrentNewsIndex: (index: number) => void
  setDailyPhrase: (phrase: PhraseItem) => void
  setDailySpeech: (speech: SpeechItem) => void
  setDailyDialogue: (dialogue: DialogueItem) => void
  setGameSession: (session: GameSession | null) => void
  setIsPlaying: (playing: boolean) => void
  setLearningMode: (mode: LearningMode) => void
}

const defaultPreferences: UserPreferences = {
  language: 'zh',
  newsCategories: ['tech', 'health'],
  speechRate: 1.0,
  phraseLanguage: 'en',
  learningLevel: 'intermediate',
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentPage: 'home',
      preferences: defaultPreferences,
      newsItems: [],
      currentNewsIndex: 0,
      dailyPhrase: null,
      dailySpeech: null,
      dailyDialogue: null,
      gameSession: null,
      isPlaying: false,
      learningMode: 'phrase',

      setPage: (page) => set({ currentPage: page }),
      setPreferences: (prefs) => set((state) => ({
        preferences: { ...state.preferences, ...prefs }
      })),
      setNewsItems: (items) => set({ newsItems: items, currentNewsIndex: 0 }),
      setCurrentNewsIndex: (index) => set({ currentNewsIndex: index }),
      setDailyPhrase: (phrase) => set({ dailyPhrase: phrase }),
      setDailySpeech: (speech) => set({ dailySpeech: speech }),
      setDailyDialogue: (dialogue) => set({ dailyDialogue: dialogue }),
      setGameSession: (session) => set({ gameSession: session }),
      setIsPlaying: (playing) => set({ isPlaying: playing }),
      setLearningMode: (mode) => set({ learningMode: mode }),
    }),
    {
      name: 'eyerest-storage',
      partialize: (state) => ({ preferences: state.preferences, learningMode: state.learningMode }),
    }
  )
)