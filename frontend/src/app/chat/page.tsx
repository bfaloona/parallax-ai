'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated, logout } from '@/lib/auth'
import { getCurrentUser, getConversations, getConversation, createConversation, addMessage } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Card } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import type { User, Conversation, Message } from '@/types'

export default function ChatPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversation, setActiveConversation] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [sending, setSending] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
      return
    }

    const init = async () => {
      try {
        const userData = await getCurrentUser()
        setUser(userData)

        const convos = await getConversations()
        setConversations(convos)

        // Auto-select first conversation or create one
        if (convos.length > 0) {
          setActiveConversation(convos[0].id)
        } else {
          const newConvo = await createConversation()
          setConversations([newConvo])
          setActiveConversation(newConvo.id)
        }
      } catch (err) {
        logout()
      } finally {
        setLoading(false)
      }
    }

    init()
  }, [router])

  // Load messages when active conversation changes
  useEffect(() => {
    if (!activeConversation) return

    const loadMessages = async () => {
      try {
        const convoWithMessages = await getConversation(activeConversation)
        setMessages(convoWithMessages.messages)
      } catch (err) {
        console.error('Failed to load messages:', err)
        setMessages([])
      }
    }

    loadMessages()
  }, [activeConversation])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || !activeConversation || sending) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setSending(true)

    // Create temporary assistant message for streaming
    const tempAssistantMsg: Message = {
      id: 'temp-' + Date.now(),
      conversation_id: activeConversation,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    }

    try {
      // Messages will be refreshed from database after streaming completes
      // For now, just stream the response
      setMessages(prev => [...prev, tempAssistantMsg])

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('parallax_token')

      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          conversation_id: activeConversation,
          message: userMessage,
          mode: 'balanced',
          model: 'haiku',
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No response body')
      }

      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (!data) continue

            try {
              const parsed = JSON.parse(data)

              if (parsed.content) {
                accumulatedContent += parsed.content
                // Update the temporary message with accumulated content
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === tempAssistantMsg.id
                      ? { ...msg, content: accumulatedContent }
                      : msg
                  )
                )
              }

              if (parsed.done) {
                // Stream completed - reload messages from database
                const convoWithMessages = await getConversation(activeConversation)
                setMessages(convoWithMessages.messages)
                break
              }

              if (parsed.error) {
                throw new Error(parsed.error)
              }
            } catch (parseErr) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (err) {
      console.error('Failed to send message:', err)
      // Remove the temporary assistant message on error
      setMessages(prev => prev.filter(msg => msg.id !== tempAssistantMsg.id))
    } finally {
      setSending(false)
    }
  }

  const handleNewConversation = async () => {
    try {
      const newConvo = await createConversation()
      setConversations(prev => [newConvo, ...prev])
      setActiveConversation(newConvo.id)
      setMessages([])
    } catch (err) {
      console.error('Failed to create conversation:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    )
  }

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 border-r bg-muted/10 flex flex-col">
        <div className="p-4 border-b">
          <Button onClick={handleNewConversation} className="w-full">
            New Conversation
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {conversations.map(convo => (
              <button
                key={convo.id}
                onClick={() => setActiveConversation(convo.id)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  activeConversation === convo.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                }`}
              >
                {convo.title}
              </button>
            ))}
          </div>
        </ScrollArea>

        <div className="p-4 border-t space-y-2">
          <div className="text-sm text-muted-foreground truncate">
            {user?.email}
          </div>
          <Button onClick={logout} variant="outline" size="sm" className="w-full">
            Logout
          </Button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-12">
                <p className="text-lg">Start a conversation</p>
                <p className="text-sm">Type a message below to begin</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="text-xs font-semibold text-muted-foreground uppercase">
                    {msg.role === 'user' ? 'You' : 'Assistant'}
                  </div>
                  <Card className="p-4">
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </Card>
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t bg-background">
          <div className="max-w-3xl mx-auto p-4">
            <form onSubmit={handleSendMessage} className="space-y-2">
              <Textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                className="min-h-[100px] resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage(e)
                  }
                }}
              />
              <div className="flex justify-end">
                <Button type="submit" disabled={sending || !inputMessage.trim()}>
                  {sending ? 'Sending...' : 'Send'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
