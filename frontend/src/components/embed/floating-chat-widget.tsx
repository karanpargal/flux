"use client";

import { Agent, Organization } from "@/lib/types";
import { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

interface Message {
    id: string;
    content: string;
    sender: "user" | "agent";
    timestamp: Date;
}

interface ChatResponse {
    success: boolean;
    data: {
        content: string;
        role: string;
        user_id: string;
        agent_id: string;
        org_id: string;
    };
}

export default function FloatingChatWidget({ agentId }: { agentId: string }) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [agent, setAgent] = useState<Agent | null>(null);
    const [organization, setOrganization] = useState<Organization | null>(null);
    const [userId, setUserId] = useState<string>("");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Generate or retrieve user ID from localStorage
    useEffect(() => {
        const getOrCreateUserId = () => {
            try {
                let storedUserId = localStorage.getItem("supportify_user_id");
                if (!storedUserId) {
                    storedUserId = uuidv4();
                    localStorage.setItem("supportify_user_id", storedUserId);
                }
                setUserId(storedUserId);
            } catch (error) {
                console.error("Error accessing localStorage:", error);
                // Fallback to session-based ID if localStorage fails
                setUserId(uuidv4());
            }
        };

        getOrCreateUserId();
    }, []);

    // Fetch agent and organization details
    useEffect(() => {
        const fetchAgentAndOrg = async () => {
            try {
                const baseUrl =
                    process.env.NEXT_PUBLIC_API_BASE_URL ||
                    "http://localhost:7990";

                // Fetch agent details
                const agentResponse = await fetch(
                    `${baseUrl}/api/v1/agents/${agentId}`
                );
                const agentData = await agentResponse.json();

                if (agentData.success) {
                    setAgent(agentData.data);

                    // Fetch organization details using the agent's org_id
                    const orgResponse = await fetch(
                        `${baseUrl}/api/v1/orgs/${agentData.data.org_id}`
                    );
                    const orgData = await orgResponse.json();

                    if (orgData.success) {
                        setOrganization(orgData.data);
                    }
                }
            } catch (error) {
                console.error("Error fetching agent/organization:", error);
            }
        };

        if (agentId && userId) {
            fetchAgentAndOrg();
        }
    }, [agentId, userId]);

    // Fetch conversation history
    useEffect(() => {
        const fetchConversationHistory = async () => {
            if (!userId || !agentId || !agent?.org_id) return;

            try {
                const baseUrl =
                    process.env.NEXT_PUBLIC_API_BASE_URL ||
                    "http://localhost:7990";
                const response = await fetch(
                    `${baseUrl}/api/v1/conversations/history?user_id=${encodeURIComponent(
                        userId
                    )}&agent_id=${encodeURIComponent(
                        agentId
                    )}&org_id=${encodeURIComponent(agent.org_id)}`
                );

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (data.success && data.data) {
                    const historyMessages: Message[] = data.data.map(
                        (msg: {
                            chat_messages_id: string;
                            content: string;
                            role: string;
                            created_at: string;
                        }) => ({
                            id: msg.chat_messages_id,
                            content: msg.content,
                            sender: msg.role === "user" ? "user" : "agent",
                            timestamp: new Date(msg.created_at),
                        })
                    );
                    setMessages(historyMessages);
                }
            } catch (error) {
                console.error("Error fetching conversation history:", error);
            }
        };

        if (userId && agentId && agent?.org_id) {
            fetchConversationHistory();
        }
    }, [userId, agentId, agent?.org_id]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim() || isLoading || !agent) return;

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
            const baseUrl =
                process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:7990";
            const response = await fetch(`${baseUrl}/api/v1/conversations`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    content: inputValue,
                    user_id: userId,
                    agent_id: agentId,
                    org_id: agent.org_id,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: ChatResponse = await response.json();

            if (data.success) {
                const agentResponse: Message = {
                    id: (Date.now() + 1).toString(),
                    content: data.data.content,
                    sender: "agent",
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, agentResponse]);
            } else {
                throw new Error("Failed to get response from agent");
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

    const adjustTextareaHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = "auto";
            textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
        }
    };

    useEffect(() => {
        adjustTextareaHeight();
    }, [inputValue]);

    return (
        <div className="floating-widget">
            {!isOpen && (
                <button
                    className="floating-widget-button"
                    onClick={() => setIsOpen(true)}
                    aria-label="Open chat"
                >
                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H5.17L4 17.17V4H20V16Z"
                            fill="currentColor"
                        />
                        <path
                            d="M7 9H17V11H7V9ZM7 12H15V14H7V12Z"
                            fill="currentColor"
                        />
                    </svg>
                </button>
            )}

            {isOpen && (
                <div className="floating-widget-chat">
                    <div className="floating-chat-header">
                        <div className="floating-chat-title">
                            <div className="flex flex-col">
                                <h3 className="font-semibold text-base m-0">
                                    {agent?.name || "AI Assistant"}
                                </h3>
                                {organization?.name && (
                                    <p className="text-sm opacity-80 m-0 mt-1">
                                        {organization.name}
                                        {organization.industry && (
                                            <span className="ml-2 text-xs opacity-60">
                                                • {organization.industry}
                                            </span>
                                        )}
                                    </p>
                                )}
                            </div>
                        </div>
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
                                    <div className="markdown-content">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            rehypePlugins={[rehypeHighlight]}
                                            components={{
                                                // Prevent new windows for links in embedded widget
                                                a: ({ node, ...props }) => (
                                                    <a {...props} target="_blank" rel="noopener noreferrer" />
                                                ),
                                                // Ensure code blocks don't break layout
                                                pre: ({ node, ...props }) => (
                                                    <pre {...props} style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }} />
                                                ),
                                            }}
                                        >
                                            {message.content}
                                        </ReactMarkdown>
                                    </div>
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
                            ref={textareaRef}
                            className="floating-chat-input"
                            placeholder="Type your message..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
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
