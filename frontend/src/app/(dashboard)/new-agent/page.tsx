"use client";

import React, { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import AgentForm from "@/components/forms/agent-form";
import { Agent } from "@/lib/types";

function NewAgentPageContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    // const createAgent = useCreateAgent(); // Unused for now

    // Get organization ID from URL search params
    const orgId = searchParams.get("orgId");
    const orgName = searchParams.get("orgName") || "Organization";

    const handleFormSubmit = async (values: Agent) => {
        // Form submission is handled by the form component
        console.log("Form submitted with values:", values);
    };

    const handleSuccess = () => {
        // Navigate to dashboard after successful creation
        router.push(`/dashboard?orgId=${orgId}`);
    };

    // Show error if no organization ID is provided
    if (!orgId) {
        return (
            <div className="min-h-screen bg-stone-50">
                <div className="max-w-4xl mx-auto px-4 py-8">
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <p className="text-red-600">
                            No organization ID provided. Please access this page
                            with a valid organization ID.
                        </p>
                        <Link
                            href="/dashboard"
                            className="text-red-500 hover:text-red-600 font-medium mt-2 inline-block"
                        >
                            ← Back to Dashboard
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-stone-50">
            <div className="max-w-4xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <Link
                            href={`/dashboard?orgId=${orgId}`}
                            className="text-stone-400 hover:text-stone-600 transition-colors"
                        >
                            ← Back to Dashboard
                        </Link>
                    </div>
                    <h1 className="text-3xl font-bold text-stone-500 mb-2">
                        Create New Agent
                    </h1>
                    <p className="text-stone-400">
                        Set up a new support agent with capabilities and context
                    </p>
                </div>

                {/* Agent Form */}
                <AgentForm
                    onSubmit={handleFormSubmit}
                    onSuccess={handleSuccess}
                    orgId={orgId}
                    orgName={orgName}
                />
            </div>
        </div>
    );
}

export default function NewAgentPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <NewAgentPageContent />
        </Suspense>
    );
}
