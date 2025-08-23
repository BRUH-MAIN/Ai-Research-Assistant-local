import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm';
import type { Message } from '../types/types'

type ChatWindowProps = {
    messages: Message[];
}

function Chat({ messages }: ChatWindowProps) {
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div
        className="w-full max-w-3xl p-4 space-y-4 bg-transparent"   
    >
        {messages.map((msg) =>  (
            <div
            key = {msg.id}
            className={`flex ${
            msg.sender === 'user' ? 'justify-end' : 'justify-start'
          }`}
            >
                <div
                className={` px-4 py-2 rounded-2xl whitespace-pre-wrap break-words 
                ${
                    msg.sender === 'user'
                    ? 'bg-gray-900 text-white rounded-br-none max-w-[75%]'
                    : 'bg-transparent text-gray-100 rounded-bl-none max-w-[100%]'
                }
                `}
                >
                    {msg.sender === 'ai' ? (
                        <div className="markdown-content">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {msg.content}
                            </ReactMarkdown>
                        </div>
                    ) : (
                        msg.content
                    )}
                </div>
            </div>
        ))}
        <div ref={chatEndRef} />
    </div>
  )
}

export default Chat
