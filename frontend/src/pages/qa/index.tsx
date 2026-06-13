import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  Send,
  Bot,
  User,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  Loader2,
  MessageSquare,
  Plus,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { qaApi } from '@/lib/api'
import { toast } from 'sonner'
import type { QARequest } from '@/types'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  timestamp: Date
}

export default function QA() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const qaMutation = useMutation({
    mutationFn: (data: QARequest) => qaApi.ask(data),
    onSuccess: (response) => {
      const { answer, sources } = response.data.data
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: answer,
        sources,
        timestamp: new Date(),
      }

      // 模拟打字机效果
      setIsTyping(true)
      let currentText = ''
      const words = answer.split('')
      let index = 0

      const typeInterval = setInterval(() => {
        if (index < words.length) {
          currentText += words[index]
          setMessages((prev) => {
            const newMessages = [...prev]
            const lastMessage = newMessages[newMessages.length - 1]
            if (lastMessage.role === 'assistant') {
              lastMessage.content = currentText
            }
            return newMessages
          })
          index++
        } else {
          clearInterval(typeInterval)
          setIsTyping(false)
        }
      }, 20)

      setMessages((prev) => [...prev, assistantMessage])
    },
    onError: (error: Error) => {
      toast.error(error.message)
      setIsTyping(false)
    },
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    const question = input.trim()
    if (!question || qaMutation.isPending) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    qaMutation.mutate({ question })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleCopy = (content: string, id: string) => {
    navigator.clipboard.writeText(content)
    setCopiedId(id)
    toast.success('已复制到剪贴板')
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleNewChat = () => {
    setMessages([])
    setInput('')
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Sidebar - Chat History */}
      <Card className="w-64 flex-shrink-0 hidden lg:flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">对话历史</CardTitle>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={handleNewChat}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="space-y-2">
            <div className="flex items-center gap-2 p-2 rounded-md bg-accent">
              <MessageSquare className="h-4 w-4 text-primary" />
              <span className="text-sm">当前对话</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Chat Area */}
      <Card className="flex-1 flex flex-col">
        <CardHeader className="pb-3 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary" />
              </div>
              <div>
                <CardTitle className="text-base">智能问答助手</CardTitle>
                <p className="text-xs text-muted-foreground">
                  基于竞品知识库的智能问答
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="lg:hidden"
              onClick={handleNewChat}
            >
              <Plus className="h-4 w-4 mr-1" />
              新对话
            </Button>
          </div>
        </CardHeader>

        {/* Messages */}
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Bot className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">有什么可以帮您的？</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                我可以基于您的竞品数据回答问题，帮助您更好地了解市场竞争情况。
              </p>
              <div className="grid grid-cols-2 gap-2 mt-6 max-w-md w-full">
                {[
                  '竞品A的核心优势是什么？',
                  '我们的定价策略如何？',
                  '市场上有哪些新趋势？',
                  '如何提升产品竞争力？',
                ].map((question) => (
                  <Button
                    key={question}
                    variant="outline"
                    className="text-left h-auto py-2 px-3 text-sm"
                    onClick={() => {
                      setInput(question)
                    }}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}

                  <div
                    className={`max-w-[80%] ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    } rounded-lg p-3`}
                  >
                    {message.role === 'assistant' ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-sm">{message.content}</p>
                    )}

                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t">
                        <p className="text-xs text-muted-foreground mb-2">
                          参考来源：
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {message.sources.map((source, index) => (
                            <Badge
                              key={index}
                              variant="secondary"
                              className="text-xs"
                            >
                              {source}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-1 mt-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() =>
                            handleCopy(message.content, message.id)
                          }
                        >
                          {copiedId === message.id ? (
                            <Check className="h-3 w-3" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7">
                          <ThumbsUp className="h-3 w-3" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7">
                          <ThumbsDown className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="bg-muted rounded-lg p-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" />
                      <div
                        className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce"
                        style={{ animationDelay: '0.1s' }}
                      />
                      <div
                        className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce"
                        style={{ animationDelay: '0.2s' }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </CardContent>

        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex gap-2">
            <Input
              placeholder="输入您的问题..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={qaMutation.isPending}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || qaMutation.isPending}
            >
              {qaMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            按 Enter 发送，Shift + Enter 换行
          </p>
        </div>
      </Card>
    </div>
  )
}
