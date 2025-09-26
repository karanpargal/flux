"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardPageProps } from "../ui/types/page-types";
import { Agent } from "../ui/types/form-types";
import AgentCard from "../ui/agent-card";

const DashboardPage: React.FC<DashboardPageProps> = ({ className = "" }) => {
    const router = useRouter();
    const [activeTab, setActiveTab] = useState<"active" | "inactive">("active");
    const [agents, setAgents] = useState<Agent[]>([
        {
            id: "1",
            name: "Sarah Johnson",
            description:
                "Handles customer inquiries and provides technical support for our main products.",
            agentType: "customer-support",
            capabilities:
                "Can answer billing questions, provide technical support, handle refunds, and escalate complex issues to human agents.",
            context:
                "https://docs.example.com/billing, https://help.example.com/refunds, Company policy: All refunds must be approved by manager",
            status: "active",
            createdAt: "2024-01-15T10:00:00Z",
            updatedAt: "2024-01-15T10:00:00Z",
            queriesSolved: 127,
        },
        {
            id: "2",
            name: "Mike Chen",
            description:
                "Specializes in billing inquiries and payment processing issues.",
            agentType: "billing",
            capabilities:
                "Handles payment processing, subscription management, invoice generation, and billing disputes.",
            context:
                "https://billing.example.com/docs, Payment gateway documentation, Subscription management policies",
            status: "active",
            createdAt: "2024-01-20T14:30:00Z",
            updatedAt: "2024-01-20T14:30:00Z",
            queriesSolved: 89,
        },
        {
            id: "3",
            name: "Emily Rodriguez",
            description:
                "Manages escalated customer complaints and complex technical issues.",
            agentType: "escalation",
            capabilities:
                "Handles complex technical issues, customer complaints, and provides advanced troubleshooting support.",
            context:
                "Technical documentation, Escalation procedures, Advanced troubleshooting guides",
            status: "inactive",
            createdAt: "2024-01-10T09:15:00Z",
            updatedAt: "2024-01-25T16:45:00Z",
            queriesSolved: 203,
        },
    ]);

    const filteredAgents = agents.filter((agent) => agent.status === activeTab);

    const handleCreateAgent = () => {
        router.push("/new-agent");
    };

    const handleToggleStatus = (agent: Agent) => {
        setAgents((prev) =>
            prev.map((a) =>
                a.id === agent.id
                    ? {
                          ...a,
                          status: a.status === "active" ? "inactive" : "active",
                          updatedAt: new Date().toISOString(),
                      }
                    : a
            )
        );
    };

    const handleEditAgent = (agent: Agent) => {
        router.push(`/agent/${agent.id}`);
    };

    const handleDeleteAgent = (agent: Agent) => {
        setAgents((prev) => prev.filter((a) => a.id !== agent.id));
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header with Create Button */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-stone-500">
                        Agents
                    </h2>
                    <p className="text-stone-400">Manage your support agents</p>
                </div>
                <button
                    onClick={handleCreateAgent}
                    className="bg-citrus-500 hover:bg-citrus-600 text-white px-6 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                >
                    Create Agent
                </button>
            </div>

            {/* Tabs */}
            <div className="border-b border-stone-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab("active")}
                        className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                            activeTab === "active"
                                ? "border-citrus-500 text-citrus-600"
                                : "border-transparent text-stone-400 hover:text-stone-500 hover:border-stone-300"
                        }`}
                    >
                        Active (
                        {agents.filter((a) => a.status === "active").length})
                    </button>
                    <button
                        onClick={() => setActiveTab("inactive")}
                        className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                            activeTab === "inactive"
                                ? "border-citrus-500 text-citrus-600"
                                : "border-transparent text-stone-400 hover:text-stone-500 hover:border-stone-300"
                        }`}
                    >
                        Inactive (
                        {agents.filter((a) => a.status === "inactive").length})
                    </button>
                </nav>
            </div>

            {/* Agents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredAgents.length > 0 ? (
                    filteredAgents.map((agent) => (
                        <AgentCard
                            key={agent.id}
                            agent={agent}
                            onEdit={handleEditAgent}
                            onDelete={handleDeleteAgent}
                            onToggleStatus={handleToggleStatus}
                        />
                    ))
                ) : (
                    <div className="col-span-full text-center py-12">
                        <div className="w-16 h-16 mx-auto mb-4 bg-stone-100 rounded-full flex items-center justify-center">
                            <svg
                                className="w-8 h-8 text-stone-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                                />
                            </svg>
                        </div>
                        <h3 className="text-lg font-medium text-stone-500 mb-2">
                            No {activeTab} agents
                        </h3>
                        <p className="text-stone-400 mb-4">
                            {activeTab === "active"
                                ? "Create your first agent to get started with support operations."
                                : "No inactive agents at the moment."}
                        </p>
                        {activeTab === "active" && (
                            <button
                                onClick={handleCreateAgent}
                                className="bg-citrus-500 hover:bg-citrus-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                            >
                                Create Your First Agent
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DashboardPage;
