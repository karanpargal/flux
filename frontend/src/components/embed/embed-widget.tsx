"use client";

import { useState, useEffect, useRef } from "react";

interface Message {
  id: string;
  content: string;
  sender: "user" | "agent";
  timestamp: Date;
}

export default function EmbedWidget({ agentId }: { agentId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDashboard, setIsDashboard] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkOrigin = () => {
      try {
        const currentPath = window.location.pathname;
        const isDashboardPath =
          currentPath.includes("/dashboard") ||
          currentPath.includes("/agent") ||
          currentPath.includes("/login") ||
          currentPath.includes("/signup") ||
          currentPath.includes("/new-agent");

        const isInIframe = window !== window.parent;

        const isEmbedPath =
          currentPath === "/embed" || currentPath.startsWith("/embed?");

        if (isEmbedPath) {
          setIsDashboard(false);
        } else if (isDashboardPath && !isInIframe) {
          setIsDashboard(true);
        } else {
          setIsDashboard(false);
        }
      } catch {
        setIsDashboard(false);
      }
    };

    checkOrigin();

    if (!isDashboard) {
      setMessages([
        {
          id: "1",
          content: "Hello! I'm your AI assistant. How can I help you today?",
          sender: "agent",
          timestamp: new Date(),
        },
      ]);
    }
  }, [isDashboard]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `I received your message: "${userMessage.content}". This is a demo response. In production, this would connect to your agent service.`,
        sender: "agent",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, agentResponse]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error. Please try again.",
        sender: "agent",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isDashboard) {
    return null;
  }

  return (
    <div className="embed-widget">
      <div className="embed-chat-window">
        <div className="embed-chat-header">
          <div className="embed-chat-title">AI Assistant</div>
          <button
            className="embed-chat-close"
            onClick={() => {
              if (window.parent !== window) {
                window.parent.postMessage({ type: "EMBED_CLOSE" }, "*");
              }
            }}
          >
            ×
          </button>
        </div>

        <div className="embed-chat-content">
          <div className="embed-chat-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`embed-message ${message.sender}`}
              >
                {message.content}
              </div>
            ))}

            {isLoading && (
              <div className="embed-message agent">
                <div className="embed-loading">
                  <div className="embed-loading-dot"></div>
                  <div className="embed-loading-dot"></div>
                  <div className="embed-loading-dot"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="embed-chat-input-container">
          <textarea
            className="embed-chat-input"
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={1}
            disabled={isLoading}
          />
          <button
            className="embed-chat-send"
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
