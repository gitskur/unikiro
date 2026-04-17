import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import './ChatWindow.css'

interface Message {
  id: number
  text: string
  sender: 'user' | 'bot'
  time: string
}

const BOT_RESPONSES = [
  '안녕하세요! 무엇을 도와드릴까요? 😊',
  '좋은 질문이네요! 조금 더 자세히 말씀해 주시겠어요?',
  '네, 알겠습니다. 처리해 드리겠습니다!',
  '혹시 다른 궁금한 점이 있으신가요?',
  '감사합니다! 더 필요한 게 있으면 언제든 말씀해주세요.',
  '이 부분은 제가 확인 후 다시 안내드리겠습니다.',
  '정말 좋은 아이디어네요! 👍',
]

function getTime() {
  return new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: '안녕하세요! 무엇을 도와드릴까요? 😊', sender: 'bot', time: getTime() },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const sendMessage = () => {
    const text = input.trim()
    if (!text) return

    const userMsg: Message = {
      id: Date.now(),
      text,
      sender: 'user',
      time: getTime(),
    }

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsTyping(true)

    setTimeout(() => {
      const botMsg: Message = {
        id: Date.now() + 1,
        text: BOT_RESPONSES[Math.floor(Math.random() * BOT_RESPONSES.length)],
        sender: 'bot',
        time: getTime(),
      }
      setMessages(prev => [...prev, botMsg])
      setIsTyping(false)
    }, 800 + Math.random() * 1200)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.nativeEvent.isComposing) {
      sendMessage()
    }
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="header-avatar">🤖</div>
        <div className="header-info">
          <h2>챗봇</h2>
          <p>{isTyping ? '입력 중...' : '온라인'}</p>
        </div>
      </div>

      <div className="messages-area" role="log" aria-live="polite">
        {messages.map(msg => (
          <MessageBubble key={msg.id} text={msg.text} sender={msg.sender} time={msg.time} />
        ))}
        {isTyping && (
          <div className="typing-indicator">
            <div className="dot" />
            <div className="dot" />
            <div className="dot" />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          ref={inputRef}
          type="text"
          placeholder="메시지를 입력하세요..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          aria-label="메시지 입력"
        />
        <button onClick={sendMessage} disabled={!input.trim()} aria-label="전송">
          ➤
        </button>
      </div>
    </div>
  )
}
