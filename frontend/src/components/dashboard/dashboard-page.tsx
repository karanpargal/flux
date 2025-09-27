"use client";
import React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DashboardPageProps } from "../ui/types/page-types";
import { useAgentsForOrg, useOrganization } from "../../lib/hooks";
import AgentCard from "../ui/agent-card";

const DashboardPage: React.FC<DashboardPageProps> = ({ className = "" }) => {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Get orgId from URL params first, then from organization data
    const urlOrgId = searchParams.get("orgId");

    const {
        data: organization,
        loading: orgLoading,
        error: orgError,
    } = useOrganization(urlOrgId);

    const orgId = organization?.org_id || urlOrgId || null;

    const {
        data: agents,
        loading: agentsLoading,
        error: agentsError,
        refetch,
    } = useAgentsForOrg(orgId);

    const filteredAgents = agents || [];

    const handleCreateAgent = () => {
        if (!orgId) {
            alert("Please provide an organization ID to create an agent");
            return;
        }
        const orgName = organization?.name || "Organization";
        router.push(
            `/new-agent?orgId=${orgId}&orgName=${encodeURIComponent(orgName)}`
        );
    };

    return (
        <div className={`space-y-6 ${className}`}>
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

            {!orgId && !orgLoading && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-600">
                        No organization ID provided. Please access this page
                        with a valid organization ID.
                    </p>
                </div>
            )}

            {orgLoading && (
                <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-citrus-500 mx-auto mb-4"></div>
                    <p className="text-stone-400">Loading organization...</p>
                </div>
            )}

            {orgError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-600">
                        Error loading organization: {orgError}
                    </p>
                </div>
            )}

            {orgId && !orgLoading && !orgError && agentsLoading && (
                <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-citrus-500 mx-auto mb-4"></div>
                    <p className="text-stone-400">Loading agents...</p>
                </div>
            )}

            {orgId && !orgLoading && !orgError && agentsError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-600">
                        Error loading agents: {agentsError}
                    </p>
                    <button
                        onClick={() => refetch()}
                        className="mt-2 text-sm bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                    >
                        Retry
                    </button>
                </div>
            )}

            {orgId &&
                !orgLoading &&
                !orgError &&
                !agentsLoading &&
                !agentsError && (
                    <div className="border-b border-stone-200">
                        <div className="py-2 px-1">
                            <span className="text-sm font-medium text-stone-500">
                                All Agents ({agents?.length || 0})
                            </span>
                        </div>
                    </div>
                )}

            {orgId &&
                !orgLoading &&
                !orgError &&
                !agentsLoading &&
                !agentsError && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredAgents.length > 0 ? (
                            filteredAgents.map((agent) => (
                                <AgentCard key={agent.agent_id} agent={agent} />
                            ))
                        ) : (
                            <div className="col-span-full">
                                <div className="bg-amber-950 rounded-lg p-4">
                                    <p className="text-stone-100">
                                        No agents found, create one to get
                                        started
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                )}
        </div>
    );
};

export default DashboardPage;
