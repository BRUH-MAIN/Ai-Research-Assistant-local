export type Message = {
  id: string
  sender: 'user' | 'ai'
  content: string
}

export type MessageBlock = {
  id: string
  userMessage: string
  aiResponse: string
  timestamp: Date
  isLoading?: boolean
}