import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Search, Copy, Check, ArrowDown } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ConversationSession {
  messages: Message[];
}

interface ConversationTabProps {
  conversation: ConversationSession | null | undefined;
}

export const ConversationTab: React.FC<ConversationTabProps> = ({ conversation }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const handleCopy = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text', err);
    }
  };

  if (!conversation || conversation.messages.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center mt-4">
        <MessageSquare className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
        <p className="text-sm font-medium">No conversation</p>
        <p className="text-xs text-muted-foreground mt-1">No chat history available</p>
      </div>
    );
  }

  const filteredMessages = conversation.messages.filter((msg) =>
    msg.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="rounded-lg border flex flex-col mt-4" style={{ height: '500px' }}>
      <div className="p-3 border-b flex items-center justify-between bg-muted/30">
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search conversation..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-9"
          />
        </div>
        <Button variant="outline" size="sm" onClick={scrollToBottom} className="ml-2 gap-2 h-9" title="Scroll to bottom">
          <ArrowDown className="h-4 w-4" />
          Latest
        </Button>
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {filteredMessages.length > 0 ? (
          filteredMessages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group`}>
              <div className={`relative rounded-lg px-4 py-2.5 max-w-[85%] text-sm ${
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                <button
                  onClick={() => handleCopy(msg.content, i)}
                  className={`absolute top-2 -right-10 p-1.5 rounded-md hover:bg-muted transition-opacity opacity-0 group-hover:opacity-100 ${
                    msg.role === 'user' ? '-left-10 right-auto' : ''
                  }`}
                  title="Copy message"
                >
                  {copiedIndex === i ? (
                    <Check className="h-3.5 w-3.5 text-emerald-500" />
                  ) : (
                    <Copy className="h-3.5 w-3.5 text-muted-foreground hover:text-foreground" />
                  )}
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-muted-foreground text-sm mt-10">
            No messages match your search.
          </div>
        )}
      </div>
    </div>
  );
};
