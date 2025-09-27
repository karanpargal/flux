"use client";

import { useState, useEffect, useRef } from "react";
import "./floating-chat-widget.css";

interface Message {
    id: string;
    content: string;
    sender: "user" | "agent";
    timestamp: Date;
}

interface FloatingChatWidgetProps {
    embedUrl?: string;
    agentId?: string;
    organizationId?: string;
    title?: string;
}

export default function FloatingChatWidget({
    embedUrl = "http://localhost:3000/embed",
    agentId,
    organizationId,
    title = "AI Assistant",
}: FloatingChatWidgetProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [hasNewMessage, setHasNewMessage] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    // Initialize with welcome message
    useEffect(() => {
        setMessages([
            {
                id: "1",
                content:
                    "Hello! I'm your AI assistant. How can I help you today?",
                sender: "agent",
                timestamp: new Date(),
            },
        ]);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

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
            // Simulate API call - replace with actual API call
            await new Promise((resolve) => setTimeout(resolve, 1000));

            const agentResponse: Message = {
                id: (Date.now() + 1).toString(),
                content: `I received your message: "${userMessage.content}". This is a demo response. In production, this would connect to your agent service.`,
                sender: "agent",
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, agentResponse]);

            // Show pulse animation for new message
            if (!isOpen) {
                setHasNewMessage(true);
                setTimeout(() => setHasNewMessage(false), 2000);
            }
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

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputValue(e.target.value);

        // Auto-resize textarea
        const textarea = e.target;
        textarea.style.height = "auto";
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
    };

    const toggleChat = () => {
        setIsOpen(!isOpen);
        setHasNewMessage(false);
    };

    return (
        <div className="floating-chat-container">
            {/* Floating Chat Button */}
            <button
                onClick={toggleChat}
                className={`floating-chat-button ${
                    hasNewMessage ? "has-new-message" : ""
                }`}
                aria-label={isOpen ? "Close chat" : "Open chat"}
            >
                {isOpen ? (
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                        />
                    </svg>
                ) : (
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                        />
                    </svg>
                )}
            </button>

            {/* Chat Widget Window */}
            {isOpen && (
                <div className="floating-chat-window">
                    <div className="floating-chat-header">
                        <h3 className="floating-chat-title">{title}</h3>
                        <button
                            className="floating-chat-close"
                            onClick={() => setIsOpen(false)}
                            aria-label="Close chat"
                        >
                            ×
                        </button>
                    </div>

                    <div className="floating-chat-content">
                        <div className="floating-chat-messages">
                            {messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`floating-message ${message.sender}`}
                                >
                                    {message.content}
                                </div>
                            ))}

                            {isLoading && (
                                <div className="floating-message agent">
                                    <div className="floating-loading">
                                        <div className="floating-loading-dot"></div>
                                        <div className="floating-loading-dot"></div>
                                        <div className="floating-loading-dot"></div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    <div className="floating-chat-input-container">
                        <textarea
                            ref={inputRef}
                            className="floating-chat-input"
                            placeholder="Type your message..."
                            value={inputValue}
                            onChange={handleInputChange}
                            onKeyPress={handleKeyPress}
                            rows={1}
                            disabled={isLoading}
                        />
                        <button
                            className="floating-chat-send"
                            onClick={handleSendMessage}
                            disabled={isLoading || !inputValue.trim()}
                        >
                            Send
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
