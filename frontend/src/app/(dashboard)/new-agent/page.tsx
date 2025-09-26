"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import Link from "next/link";

const agentTypes = [
    { value: "customer-support", label: "Customer Support" },
    { value: "technical-support", label: "Technical Support" },
    { value: "sales", label: "Sales" },
    { value: "billing", label: "Billing" },
    { value: "general", label: "General" },
    { value: "escalation", label: "Escalation" },
];

interface AgentFormValues {
    name: string;
    description: string;
    agentType: string;
    capabilities: string;
    context: string;
}

const validationSchema = Yup.object({
    name: Yup.string()
        .min(2, "Agent name must be at least 2 characters")
        .max(50, "Agent name must be less than 50 characters")
        .required("Agent name is required"),
    description: Yup.string()
        .min(10, "Description must be at least 10 characters")
        .max(500, "Description must be less than 500 characters")
        .required("Description is required"),
    agentType: Yup.string().required("Agent type is required"),
    capabilities: Yup.string()
        .min(10, "Capabilities must be at least 10 characters")
        .max(1000, "Capabilities must be less than 1000 characters")
        .required("Capabilities are required"),
    context: Yup.string()
        .min(10, "Context must be at least 10 characters")
        .max(2000, "Context must be less than 2000 characters")
        .required("Context is required"),
});

export default function NewAgentPage() {
    const router = useRouter();
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        reset,
    } = useForm<AgentFormValues>({
        resolver: yupResolver(validationSchema),
    });

    const handleFormSubmit = async (values: AgentFormValues) => {
        try {
            // TODO: Replace with actual API call
            const newAgent = {
                id: Date.now().toString(),
                ...values,
                status: "active",
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
            };

            // Simulate API call
            await new Promise((resolve) => setTimeout(resolve, 1000));

            // Navigate to agent interface page
            router.push(`/agent/${newAgent.id}`);
        } catch (error) {
            console.error("Error creating agent:", error);
        }
    };

    return (
        <div className="min-h-screen bg-stone-50">
            <div className="max-w-4xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <Link
                            href="/dashboard"
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

                {/* Form */}
                <div className="bg-white p-8 rounded-lg shadow-lg border border-stone-200">
                    <form
                        onSubmit={handleSubmit(handleFormSubmit)}
                        className="space-y-6"
                    >
                        {/* Agent Name */}
                        <div>
                            <label
                                htmlFor="name"
                                className="block text-sm font-medium text-stone-500 mb-2"
                            >
                                Agent Name *
                            </label>
                            <input
                                type="text"
                                id="name"
                                {...register("name")}
                                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                                    errors.name
                                        ? "border-red-500"
                                        : "border-stone-300"
                                }`}
                                placeholder="Enter agent name"
                            />
                            {errors.name && (
                                <div className="mt-1 text-sm text-red-600">
                                    {errors.name.message}
                                </div>
                            )}
                        </div>

                        {/* Agent Type */}
                        <div>
                            <label
                                htmlFor="agentType"
                                className="block text-sm font-medium text-stone-500 mb-2"
                            >
                                Agent Type *
                            </label>
                            <select
                                id="agentType"
                                {...register("agentType")}
                                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                                    errors.agentType
                                        ? "border-red-500"
                                        : "border-stone-300"
                                }`}
                            >
                                <option value="">Select agent type</option>
                                {agentTypes.map((type) => (
                                    <option key={type.value} value={type.value}>
                                        {type.label}
                                    </option>
                                ))}
                            </select>
                            {errors.agentType && (
                                <div className="mt-1 text-sm text-red-600">
                                    {errors.agentType.message}
                                </div>
                            )}
                        </div>

                        {/* Description */}
                        <div>
                            <label
                                htmlFor="description"
                                className="block text-sm font-medium text-stone-500 mb-2"
                            >
                                Description *
                            </label>
                            <textarea
                                id="description"
                                rows={4}
                                {...register("description")}
                                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                                    errors.description
                                        ? "border-red-500"
                                        : "border-stone-300"
                                }`}
                                placeholder="Describe the agent's role and responsibilities"
                            />
                            {errors.description && (
                                <div className="mt-1 text-sm text-red-600">
                                    {errors.description.message}
                                </div>
                            )}
                        </div>

                        {/* Capabilities */}
                        <div>
                            <label
                                htmlFor="capabilities"
                                className="block text-sm font-medium text-stone-500 mb-2"
                            >
                                Agent Capabilities *
                            </label>
                            <textarea
                                id="capabilities"
                                rows={4}
                                {...register("capabilities")}
                                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                                    errors.capabilities
                                        ? "border-red-500"
                                        : "border-stone-300"
                                }`}
                                placeholder="Describe what this agent can do (e.g., answer billing questions, provide technical support, handle refunds)"
                            />
                            {errors.capabilities && (
                                <div className="mt-1 text-sm text-red-600">
                                    {errors.capabilities.message}
                                </div>
                            )}
                        </div>

                        {/* Context */}
                        <div>
                            <label
                                htmlFor="context"
                                className="block text-sm font-medium text-stone-500 mb-2"
                            >
                                Context & Knowledge Sources *
                            </label>
                            <textarea
                                id="context"
                                rows={6}
                                {...register("context")}
                                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                                    errors.context
                                        ? "border-red-500"
                                        : "border-stone-300"
                                }`}
                                placeholder="Provide context through links, documentation, or other sources. For example: 'https://docs.example.com/billing, https://help.example.com/refunds, Company policy: All refunds must be approved by manager'"
                            />
                            <div className="mt-2 text-sm text-stone-400">
                                Include relevant links, documentation URLs,
                                company policies, or any other context that will
                                help the agent provide accurate responses.
                            </div>
                            {errors.context && (
                                <div className="mt-1 text-sm text-red-600">
                                    {errors.context.message}
                                </div>
                            )}
                        </div>

                        {/* Submit Buttons */}
                        <div className="flex gap-4 pt-6">
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="flex-1 bg-citrus-500 hover:bg-citrus-600 disabled:bg-citrus-400 text-white font-medium py-3 px-6 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                            >
                                {isSubmitting
                                    ? "Creating Agent..."
                                    : "Create Agent"}
                            </button>
                            <Link
                                href="/dashboard"
                                className="px-6 py-3 border border-stone-300 text-stone-500 rounded-md hover:bg-stone-50 transition-colors focus:outline-none focus:ring-2 focus:ring-stone-500 focus:ring-offset-2"
                            >
                                Cancel
                            </Link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
