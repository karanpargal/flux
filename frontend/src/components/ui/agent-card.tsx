"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AgentCardProps } from "./types/page-types";
import { Agent } from "@/lib/types";
import { useUpdateAgentStatus } from "../../lib/hooks/use-agents";

const AgentCard: React.FC<AgentCardProps> = ({
  agent: initialAgent,
  className = "",
}) => {
  const router = useRouter();
  const { execute: updateStatus } = useUpdateAgentStatus();

  // Local state for optimistic updates
  const [agent, setAgent] = useState<Agent>(initialAgent);
  const getAgentTypeColor = (type: string) => {
    const colors = {
      "customer-support": "bg-blue-100 text-blue-800",
      "technical-support": "bg-green-100 text-green-800",
      sales: "bg-purple-100 text-purple-800",
      billing: "bg-yellow-100 text-yellow-800",
      general: "bg-gray-100 text-gray-800",
      escalation: "bg-red-100 text-red-800",
    };
    return colors[type as keyof typeof colors] || "bg-gray-100 text-gray-800";
  };

  const formatAgentType = (type: string) => {
    return type
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const handleCardClick = (e: React.MouseEvent) => {
    // Don't navigate if clicking on the toggle
    if ((e.target as HTMLElement).closest(".toggle-container")) {
      return;
    }
    router.push(`/agent/${agent.agent_id}`);
  };

  const handleToggleClick = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click

    // Optimistic update - immediately update the UI
    const newAgent = {
      ...agent,
      active: !agent.active,
    };
    setAgent(newAgent);

    try {
      const newActiveStatus = newAgent.active;
      await updateStatus(agent.agent_id, newActiveStatus);
    } catch (error) {
      console.error("Failed to update agent status:", error);
      // Revert optimistic update on error
      setAgent(agent);
      // You could add toast notification here
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-md border border-stone-200 p-6 hover:shadow-lg transition-shadow cursor-pointer ${className}`}
      onClick={handleCardClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-stone-500">
              {agent.name}
            </h3>
            <span className={`px-2 py-1 rounded-full text-xs font-medium`}>
              {Object.keys(agent.capabilities).join(", ")}
            </span>
          </div>
          <p className="text-stone-400 text-sm mb-3">{agent.description}</p>
        </div>
        <div className="toggle-container">
          <button
            onClick={handleToggleClick}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2 ${
              agent.active ? "bg-citrus-500" : "bg-gray-200"
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                agent.active ? "translate-x-4" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-xs text-stone-400">
          Created: {new Date(agent.created_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default AgentCard;
