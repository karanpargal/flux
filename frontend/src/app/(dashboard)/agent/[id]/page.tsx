"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import { Agent, AgentFormValues } from "@/components/ui/types/page-types";

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

export default function AgentInterfacePage() {
    const params = useParams();
    const router = useRouter();
    const agentId = params.id as string;

    const [agent, setAgent] = useState<Agent | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        reset,
        setValue,
    } = useForm<AgentFormValues>({
        resolver: yupResolver(validationSchema),
    });

    // Mock data - replace with actual API call
    useEffect(() => {
        const fetchAgent = async () => {
            try {
                // TODO: Replace with actual API call
                const mockAgent: Agent = {
                    id: agentId,
                    name: "Sarah Johnson",
                    description:
                        "Handles customer inquiries and provides technical support for our main products.",
                    agentType: "customer-support",
                    capabilities:
                        "Can answer billing questions, provide technical support, handle refunds, and escalate complex issues to human agents.",
                    context:
                        "https://docs.example.com/billing, https://help.example.com/refunds, Company policy: All refunds must be approved by manager. Product knowledge base: https://kb.example.com/products",
                    status: "active",
                    createdAt: "2024-01-15T10:00:00Z",
                    updatedAt: "2024-01-15T10:00:00Z",
                    queriesSolved: 127,
                };

                setAgent(mockAgent);
                setValue("name", mockAgent.name);
                setValue("description", mockAgent.description);
                setValue("agentType", mockAgent.agentType);
                setValue("capabilities", mockAgent.capabilities);
                setValue("context", mockAgent.context);
            } catch (error) {
                console.error("Error fetching agent:", error);
            } finally {
                setIsLoading(false);
            }
        };

        if (agentId) {
            fetchAgent();
        }
    }, [agentId, setValue]);

    const handleFormSubmit = async (values: AgentFormValues) => {
        try {
            // TODO: Replace with actual API call
            const updatedAgent = {
                ...agent,
                ...values,
                updatedAt: new Date().toISOString(),
            };

            setAgent(updatedAgent as Agent);
            setIsEditing(false);
        } catch (error) {
            console.error("Error updating agent:", error);
        }
    };

    const handleToggleStatus = async () => {
        if (!agent) return;

        try {
            // TODO: Replace with actual API call
            const updatedAgent = {
                ...agent,
                status: (agent.status === "active" ? "inactive" : "active") as
                    | "active"
                    | "inactive",
                updatedAt: new Date().toISOString(),
            };

            setAgent(updatedAgent);
        } catch (error) {
            console.error("Error toggling agent status:", error);
        }
    };

    const handleDeleteAgent = async () => {
        if (!agent) return;

        if (
            confirm(
                "Are you sure you want to delete this agent? This action cannot be undone."
            )
        ) {
            try {
                // TODO: Replace with actual API call
                router.push("/dashboard");
            } catch (error) {
                console.error("Error deleting agent:", error);
            }
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-stone-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-citrus-500 mx-auto mb-4"></div>
                    <p className="text-stone-400">Loading agent...</p>
                </div>
            </div>
        );
    }

    if (!agent) {
        return (
            <div className="min-h-screen bg-stone-50 flex items-center justify-center">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-stone-500 mb-4">
                        Agent Not Found
                    </h1>
                    <p className="text-stone-400 mb-6">
                        The agent you are looking for doesn&apos;t exist.
                    </p>
                    <Link
                        href="/dashboard"
                        className="bg-citrus-500 hover:bg-citrus-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                    >
                        Back to Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-stone-50">
            <div className="max-w-6xl mx-auto px-4 py-8">
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
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-stone-500 mb-2">
                                {isEditing ? "Edit Agent" : agent.name}
                            </h1>
                            <p className="text-stone-400">
                                {isEditing
                                    ? "Update agent details"
                                    : "Agent interface and management"}
                            </p>
                        </div>
                        <div className="flex gap-3">
                            {!isEditing && (
                                <>
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="bg-citrus-500 hover:bg-citrus-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                                    >
                                        Edit Agent
                                    </button>
                                    <button
                                        onClick={handleToggleStatus}
                                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                                            agent.status === "active"
                                                ? "bg-red-500 hover:bg-red-600 text-white"
                                                : "bg-green-500 hover:bg-green-600 text-white"
                                        }`}
                                    >
                                        {agent.status === "active"
                                            ? "Deactivate"
                                            : "Activate"}
                                    </button>
                                    <button
                                        onClick={handleDeleteAgent}
                                        className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                                    >
                                        Delete
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {isEditing ? (
                            /* Edit Form */
                            <div className="bg-white p-6 rounded-lg shadow-lg border border-stone-200">
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
                                        />
                                        {errors.name && (
                                            <div className="mt-1 text-sm text-red-600">
                                                {errors.name.message}
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
                                            rows={3}
                                            {...register("description")}
                                            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                                                errors.description
                                                    ? "border-red-500"
                                                    : "border-stone-300"
                                            }`}
                                        />
                                        {errors.description && (
                                            <div className="mt-1 text-sm text-red-600">
                                                {errors.description.message}
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
                                            <option value="">
                                                Select agent type
                                            </option>
                                            <option value="customer-support">
                                                Customer Support
                                            </option>
                                            <option value="technical-support">
                                                Technical Support
                                            </option>
                                            <option value="sales">Sales</option>
                                            <option value="billing">
                                                Billing
                                            </option>
                                            <option value="general">
                                                General
                                            </option>
                                            <option value="escalation">
                                                Escalation
                                            </option>
                                        </select>
                                        {errors.agentType && (
                                            <div className="mt-1 text-sm text-red-600">
                                                {errors.agentType.message}
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
                                        />
                                        {errors.context && (
                                            <div className="mt-1 text-sm text-red-600">
                                                {errors.context.message}
                                            </div>
                                        )}
                                    </div>

                                    {/* Form Actions */}
                                    <div className="flex gap-4 pt-4">
                                        <button
                                            type="submit"
                                            disabled={isSubmitting}
                                            className="bg-citrus-500 hover:bg-citrus-600 disabled:bg-citrus-400 text-white font-medium py-2 px-6 rounded-md transition-colors"
                                        >
                                            {isSubmitting
                                                ? "Saving..."
                                                : "Save Changes"}
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setIsEditing(false);
                                                reset();
                                            }}
                                            className="px-6 py-2 border border-stone-300 text-stone-500 rounded-md hover:bg-stone-50 transition-colors"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </form>
                            </div>
                        ) : (
                            /* View Mode */
                            <>
                                {/* Agent Details */}
                                <div className="bg-white p-6 rounded-lg shadow-lg border border-stone-200">
                                    <h2 className="text-xl font-semibold text-stone-500 mb-4">
                                        Agent Details
                                    </h2>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-stone-400 mb-1">
                                                Name
                                            </label>
                                            <p className="text-stone-600">
                                                {agent.name}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-stone-400 mb-1">
                                                Type
                                            </label>
                                            <p className="text-stone-600 capitalize">
                                                {agent.agentType.replace(
                                                    "-",
                                                    " "
                                                )}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-stone-400 mb-1">
                                                Description
                                            </label>
                                            <p className="text-stone-600">
                                                {agent.description}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-stone-400 mb-1">
                                                Status
                                            </label>
                                            <span
                                                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                    agent.status === "active"
                                                        ? "bg-green-100 text-green-800"
                                                        : "bg-red-100 text-red-800"
                                                }`}
                                            >
                                                {agent.status}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Capabilities */}
                                <div className="bg-white p-6 rounded-lg shadow-lg border border-stone-200">
                                    <h2 className="text-xl font-semibold text-stone-500 mb-4">
                                        Capabilities
                                    </h2>
                                    <p className="text-stone-600 whitespace-pre-wrap">
                                        {agent.capabilities}
                                    </p>
                                </div>

                                {/* Context */}
                                <div className="bg-white p-6 rounded-lg shadow-lg border border-stone-200">
                                    <h2 className="text-xl font-semibold text-stone-500 mb-4">
                                        Context & Knowledge Sources
                                    </h2>
                                    <div className="text-stone-600 whitespace-pre-wrap">
                                        {agent.context
                                            .split(",")
                                            .map((item, index) => (
                                                <div
                                                    key={index}
                                                    className="mb-2"
                                                >
                                                    {item
                                                        .trim()
                                                        .startsWith("http") ? (
                                                        <a
                                                            href={item.trim()}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-citrus-600 hover:text-citrus-700 underline"
                                                        >
                                                            {item.trim()}
                                                        </a>
                                                    ) : (
                                                        <span>
                                                            {item.trim()}
                                                        </span>
                                                    )}
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Stats */}
                        <div className="bg-white p-6 rounded-lg shadow-lg border border-stone-200">
                            <h2 className="text-xl font-semibold text-stone-500 mb-4">
                                Statistics
                            </h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-stone-400 mb-1">
                                        Queries Solved
                                    </label>
                                    <p className="text-2xl font-bold text-citrus-600">
                                        {agent.queriesSolved || 0}
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-stone-400 mb-1">
                                        Created
                                    </label>
                                    <p className="text-stone-600">
                                        {new Date(
                                            agent.createdAt
                                        ).toLocaleDateString()}
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-stone-400 mb-1">
                                        Last Updated
                                    </label>
                                    <p className="text-stone-600">
                                        {new Date(
                                            agent.updatedAt
                                        ).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="bg-white p-6 rounded-lg shadow-lg border border-stone-200">
                            <h2 className="text-xl font-semibold text-stone-500 mb-4">
                                Quick Actions
                            </h2>
                            <div className="space-y-3">
                                <button className="w-full bg-citrus-500 hover:bg-citrus-600 text-white py-2 px-4 rounded-md transition-colors">
                                    Test Agent
                                </button>
                                <button className="w-full bg-stone-500 hover:bg-stone-600 text-white py-2 px-4 rounded-md transition-colors">
                                    View Logs
                                </button>
                                <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md transition-colors">
                                    Export Data
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
