"use client";
import React from "react";
import { AgentCardProps } from "./types/page-types";

const AgentCard: React.FC<AgentCardProps> = ({
    agent,
    onEdit,
    onDelete,
    onToggleStatus,
    className = "",
}) => {
    const getAgentTypeColor = (type: string) => {
        const colors = {
            "customer-support": "bg-blue-100 text-blue-800",
            "technical-support": "bg-green-100 text-green-800",
            sales: "bg-purple-100 text-purple-800",
            billing: "bg-yellow-100 text-yellow-800",
            general: "bg-gray-100 text-gray-800",
            escalation: "bg-red-100 text-red-800",
        };
        return (
            colors[type as keyof typeof colors] || "bg-gray-100 text-gray-800"
        );
    };

    const formatAgentType = (type: string) => {
        return type
            .split("-")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    };

    return (
        <div
            className={`bg-white rounded-lg shadow-md border border-stone-200 p-6 hover:shadow-lg transition-shadow ${className}`}
        >
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-stone-500">
                            {agent.name}
                        </h3>
                        <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${getAgentTypeColor(
                                agent.agentType
                            )}`}
                        >
                            {formatAgentType(agent.agentType)}
                        </span>
                    </div>
                    <p className="text-stone-400 text-sm mb-3">
                        {agent.description}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                            agent.status === "active"
                                ? "bg-green-100 text-green-800"
                                : "bg-gray-100 text-gray-800"
                        }`}
                    >
                        {agent.status}
                    </span>
                </div>
            </div>

            <div className="flex items-center justify-between">
                <div className="text-xs text-stone-400">
                    Created: {new Date(agent.createdAt).toLocaleDateString()}
                </div>
                <div className="flex gap-2">
                    {onToggleStatus && (
                        <button
                            onClick={() => onToggleStatus(agent)}
                            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                agent.status === "active"
                                    ? "bg-gray-100 text-gray-600 hover:bg-gray-200"
                                    : "bg-green-100 text-green-600 hover:bg-green-200"
                            }`}
                        >
                            {agent.status === "active"
                                ? "Deactivate"
                                : "Activate"}
                        </button>
                    )}
                    {onEdit && (
                        <button
                            onClick={() => onEdit(agent)}
                            className="px-3 py-1 bg-citrus-100 text-citrus-600 rounded text-xs font-medium hover:bg-citrus-200 transition-colors"
                        >
                            Edit
                        </button>
                    )}
                    {onDelete && (
                        <button
                            onClick={() => onDelete(agent)}
                            className="px-3 py-1 bg-red-100 text-red-600 rounded text-xs font-medium hover:bg-red-200 transition-colors"
                        >
                            Delete
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AgentCard;
