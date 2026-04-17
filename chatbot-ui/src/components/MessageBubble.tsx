import './MessageBubble.css'

interface MessageBubbleProps {
  text: string
  sender: 'user' | 'bot'
  time: string
}

export default function MessageBubble({ text, sender, time }: MessageBubbleProps) {
  return (
    <div className={`message-row ${sender}`}>
      <div className="avatar">{sender === 'bot' ? '🤖' : '👤'}</div>
      <div>
        <div className="bubble">{text}</div>
        <div className="timestamp">{time}</div>
      </div>
    </div>
  )
}
