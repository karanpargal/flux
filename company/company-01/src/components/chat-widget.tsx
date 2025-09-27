"use client";

import { useState, useEffect, useRef } from "react";

interface ChatWidgetProps {
    embedUrl?: string;
    agentId?: string;
    organizationId?: string;
}

export default function ChatWidget({
    embedUrl = "http://localhost:3000/embed",
    agentId,
    organizationId,
}: ChatWidgetProps) {
    const [isOpen, setIsOpen] = useState(false);
    const iframeRef = useRef<HTMLIFrameElement>(null);

    useEffect(() => {
        const iframe = iframeRef.current;
        if (!iframe) return;

        const handleMessage = (event: MessageEvent) => {
            const allowedOrigins = [
                window.location.origin,
                "http://localhost:3000", // Frontend embed origin
                process.env.NEXT_PUBLIC_EMBED_ORIGIN || "http://localhost:3000",
            ];

            if (!allowedOrigins.includes(event.origin)) {
                return;
            }

            switch (event.data.type) {
                case "EMBED_RESIZE":
                    if (iframe && event.data.height) {
                        iframe.style.height = `${event.data.height}px`;
                    }
                    break;
                case "EMBED_READY":
                    console.log("Embed widget is ready");
                    break;
                case "EMBED_CLOSE":
                    setIsOpen(false);
                    break;
                default:
                    break;
            }
        };

        window.addEventListener("message", handleMessage);

        return () => {
            window.removeEventListener("message", handleMessage);
        };
    }, []);

    const getEmbedUrl = () => {
        const params = new URLSearchParams();
        if (agentId) params.append("agentId", agentId);
        if (organizationId) params.append("orgId", organizationId);
        return `${embedUrl}?${params.toString()}`;
    };

    return (
        <>
            {/* Floating Chat Button */}
            <div className="fixed bottom-6 right-6 z-50">
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group"
                    aria-label="Open chat"
                >
                    {isOpen ? (
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    ) : (
                        <svg
                            className="w-6 h-6 group-hover:scale-110 transition-transform duration-200"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            />
                        </svg>
                    )}
                </button>
            </div>

            {/* Embed Widget */}
            {isOpen && (
                <div className="fixed bottom-24 right-6 z-50 w-80 h-96 bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
                    <iframe
                        ref={iframeRef}
                        src={getEmbedUrl()}
                        width="100%"
                        height="100%"
                        className="border-none rounded-xl"
                        style={{
                            border: "none",
                            borderRadius: "12px",
                        }}
                        title="AI Assistant Chat Widget"
                        allow="microphone; camera"
                        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                    />
                </div>
            )}
        </>
    );
}
