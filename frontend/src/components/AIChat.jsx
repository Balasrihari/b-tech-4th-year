import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { agentsService } from '../services/agents';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';

const AIChat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI academic assistant. I can help you with:\n\n• Academic questions and concept explanations\n• Document-based Q&A with citations\n• Coding help and code explanations\n• Quiz generation for test preparation\n• Study planning and scheduling\n• Learning analytics and performance insights\n\nHow can I assist you today?',
    }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const chatMutation = useMutation({
    mutationFn: agentsService.chat,
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          agent_used: data.agent_used,
          context: data.context,
        },
      ]);
    },
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || chatMutation.isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    chatMutation.mutate(userMessage);
  };

  const formatMessage = (content) => {
    // Convert markdown-like formatting to HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-700 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br />');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg">
            <Sparkles size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold">AI Academic Assistant</h2>
            <p className="text-sm text-blue-100">Multi-agent system powered by LangGraph</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <Bot size={16} className="text-white" />
              </div>
            )}
            <div
              className={`max-w-[70%] rounded-lg p-4 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 shadow-md border border-gray-200 dark:border-gray-700'
              }`}
            >
              {msg.role === 'assistant' && msg.agent_used && (
                <div className="text-xs text-blue-600 dark:text-blue-400 mb-2 font-medium">
                  Agent: {msg.agent_used}
                </div>
              )}
              <div
                className={`text-sm leading-relaxed ${
                  msg.role === 'user' ? 'text-white' : 'text-gray-800 dark:text-gray-200'
                }`}
                dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
              />
            </div>
            {msg.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                <User size={16} className="text-gray-700 dark:text-gray-300" />
              </div>
            )}
          </div>
        ))}
        {chatMutation.isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-white dark:bg-gray-800 shadow-md border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Loader2 size={16} className="animate-spin text-blue-600" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 rounded-b-lg">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about your studies..."
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            disabled={chatMutation.isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || chatMutation.isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {chatMutation.isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Try: "Explain machine learning", "Generate a quiz on Python", "Create a study plan for calculus"
        </div>
      </form>
    </div>
  );
};

export default AIChat;
