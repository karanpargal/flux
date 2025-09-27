"use client";

import FloatingChatWidget from "@/components/embed/floating-chat-widget";
import "@/components/embed/floating-chat-widget.css";

interface EmbedPageProps {
  params: {
    agent_id: string;
  };
}

export default function EmbedPage({ params }: EmbedPageProps) {
  return <FloatingChatWidget agentId={params.agent_id} />;
}
