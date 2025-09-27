"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import { useAgent, useUpdateAgent, useDeleteAgent } from "@/lib/hooks";

const validationSchema = Yup.object({
    name: Yup.string()
        .min(2, "Agent name must be at least 2 characters")
        .max(50, "Agent name must be less than 50 characters")
        .required("Agent name is required"),
    description: Yup.string()
        .min(10, "Description must be at least 10 characters")
        .max(500, "Description must be less than 500 characters")
        .nullable()
        .optional(),
    org_id: Yup.string().required("Organization ID is required"),
    org_name: Yup.string().required("Organization name is required"),
});

export default function AgentInterfacePage() {
    const params = useParams();
    const router = useRouter();
    const agentId = params.id as string;

    const [isEditing, setIsEditing] = useState(false);

    // Use real API hooks
    const {
        data: agent,
        loading: agentLoading,
        error: agentError,
        refetch,
    } = useAgent(agentId);
    const updateAgent = useUpdateAgent();
    const deleteAgent = useDeleteAgent();

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        reset,
        setValue,
    } = useForm({
        resolver: yupResolver(validationSchema),
    });

    // Update form values when agent data loads
    React.useEffect(() => {
        if (agent) {
            setValue("name", agent.name);
            setValue("description", agent.description || "");
            setValue("org_id", agent.org_id);
            setValue("org_name", "Demo Organization"); // This would come from org context
        }
    }, [agent, setValue]);

    const handleFormSubmit = async (values: {
        name: string;
        description?: string | null | undefined;
        org_id: string;
        org_name: string;
    }) => {
        try {
            await updateAgent.execute(agentId, {
                name: values.name,
                description: values.description || undefined,
            });
            setIsEditing(false);
            refetch(); // Refresh agent data
        } catch (error) {
            console.error("Error updating agent:", error);
        }
    };

    const handleToggleStatus = async () => {
        // Since our backend doesn't have status field, we'll just show a message
        console.log("Status toggle not implemented in backend yet");
        // In the future, this would call an update API
    };

    const handleDeleteAgent = async () => {
        if (!agent) return;

        if (
            confirm(
                "Are you sure you want to delete this agent? This action cannot be undone."
            )
        ) {
            try {
                await deleteAgent.execute(agentId);
                router.push(`/dashboard?orgId=${agent.org_id}`);
            } catch (error) {
                console.error("Error deleting agent:", error);
            }
        }
    };

    if (agentLoading) {
        return (
            <div className="min-h-screen bg-stone-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-citrus-500 mx-auto mb-4"></div>
                    <p className="text-stone-400">Loading agent...</p>
                </div>
            </div>
        );
    }

    if (agentError) {
        return (
            <div className="min-h-screen bg-stone-50 flex items-center justify-center">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-stone-500 mb-4">
                        Error Loading Agent
                    </h1>
                    <p className="text-stone-400 mb-6">{agentError}</p>
                    <div className="space-x-4">
                        <button
                            onClick={() => refetch()}
                            className="bg-citrus-500 hover:bg-citrus-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                        >
                            Retry
                        </button>
                        <Link
                            href={`/dashboard?orgId=${agent?.org_id || ""}`}
                            className="bg-stone-500 hover:bg-stone-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                        >
                            Back to Dashboard
                        </Link>
                    </div>
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
                            href={`/dashboard?orgId=${agent?.org_id}`}
                            className="text-stone-400 hover:text-stone-600 transition-colors"
                        >
                            ← Back to Dashboard
                        </Link>
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-stone-500 mb-2">
                                {isEditing ? "Edit Agent" : agent?.name}
                            </h1>
                            <p className="text-stone-400">
                                {isEditing
                                    ? "Update agent details"
                                    : "Agent interface and management"}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-stretch gap-8 glass-effect-citrus p-8 rounded-3xl">
                    {/* Main Content */}
                    <div className="space-y-6 w-full flex flex-col">
                        {isEditing ? (
                            /* Edit Form */
                            <div className="bg-white p-6 rounded-lg shadow-lg border border-stone-200">
                                <form
                                    onSubmit={handleSubmit(handleFormSubmit)}
                                    className="space-y-6"
                                >
                                    {/* Hidden fields for org info */}
                                    <input
                                        type="hidden"
                                        {...register("org_id")}
                                    />
                                    <input
                                        type="hidden"
                                        {...register("org_name")}
                                    />

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
                                            rows={4}
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

                                    {/* Error Display */}
                                    {updateAgent.error && (
                                        <div className="p-4 border border-red-300 bg-red-50 rounded-md">
                                            <p className="text-sm text-red-600">
                                                {updateAgent.error}
                                            </p>
                                        </div>
                                    )}

                                    {/* Form Actions */}
                                    <div className="flex gap-4 pt-4">
                                        <button
                                            type="submit"
                                            disabled={
                                                isSubmitting ||
                                                updateAgent.loading
                                            }
                                            className="bg-citrus-500 hover:bg-citrus-600 disabled:bg-citrus-400 text-white font-medium py-2 px-6 rounded-md transition-colors"
                                        >
                                            {isSubmitting || updateAgent.loading
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
                            <div className="w-full flex-1">
                                {/* Agent Details */}
                                <div className="bg-white w-full  py-6 rounded-lg shadow-lg border border-stone-200 h-full">
                                    <h2 className="text-xl border-b px-6 pb-4 font-semibold text-stone-500 mb-4">
                                        Agent Details
                                    </h2>
                                    <div className="space-y-4 px-6">
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Name
                                            </label>
                                            <p className="text-stone-600 text-lg">
                                                {agent?.name}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Description
                                            </label>
                                            <p className="text-stone-600 text-lg">
                                                {agent?.description ||
                                                    "No description provided"}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Agent ID
                                            </label>
                                            <p className="text-lg text-stone-500 font-mono bg-stone-50 p-2 rounded">
                                                {agent?.agent_id}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Organization ID
                                            </label>
                                            <p className="text-lg text-stone-500 font-mono bg-stone-50 p-2 rounded">
                                                {agent?.org_id}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Created At
                                            </label>
                                            <p className="text-stone-600 text-lg">
                                                {agent?.created_at
                                                    ? new Date(
                                                          agent.created_at
                                                      ).toLocaleString()
                                                    : "N/A"}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Status
                                            </label>
                                            <p className="text-stone-600 text-lg">
                                                <span
                                                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                        agent?.active
                                                            ? "bg-green-100 text-green-800"
                                                            : "bg-red-100 text-red-800"
                                                    }`}
                                                >
                                                    {agent?.active
                                                        ? "Active"
                                                        : "Inactive"}
                                                </span>
                                            </p>
                                        </div>
                                        {agent?.resource_urls &&
                                            agent.resource_urls.length > 0 && (
                                                <div>
                                                    <label className="block text-base font-medium text-stone-400 mb-1">
                                                        Resource URLs
                                                    </label>
                                                    <div className="space-y-2">
                                                        {agent.resource_urls.map(
                                                            (url, index) => (
                                                                <div
                                                                    key={index}
                                                                    className="flex items-center gap-2"
                                                                >
                                                                    <a
                                                                        href={
                                                                            url
                                                                        }
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="text-citrus-500 hover:text-citrus-600 text-lg break-all"
                                                                    >
                                                                        {url}
                                                                    </a>
                                                                </div>
                                                            )
                                                        )}
                                                    </div>
                                                </div>
                                            )}
                                        {agent?.file_urls &&
                                            agent.file_urls.length > 0 && (
                                                <div>
                                                    <label className="block text-sm font-medium text-stone-400 mb-1">
                                                        Uploaded Files
                                                    </label>
                                                    <div className="space-y-2">
                                                        {agent.file_urls.map(
                                                            (
                                                                fileUrl,
                                                                index
                                                            ) => (
                                                                <div
                                                                    key={index}
                                                                    className="flex items-center gap-2"
                                                                >
                                                                    <a
                                                                        href={
                                                                            fileUrl
                                                                        }
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="text-citrus-500 hover:text-citrus-600 text-lg break-all"
                                                                    >
                                                                        {fileUrl
                                                                            .split(
                                                                                "/"
                                                                            )
                                                                            .pop() ||
                                                                            `File ${
                                                                                index +
                                                                                1
                                                                            }`}
                                                                    </a>
                                                                </div>
                                                            )
                                                        )}
                                                    </div>
                                                </div>
                                            )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6 flex flex-col ">
                        {/* Stats */}
                        <div className="bg-white py-6 w-96 rounded-lg shadow-lg border border-stone-200">
                            <h2 className="text-xl px-6 border-b pb-4 font-semibold text-stone-500 mb-4">
                                Agent Information
                            </h2>
                            <div className="space-y-4 px-6">
                                <div>
                                    <label className="block text-base font-medium text-stone-400 mb-1">
                                        Agent ID
                                    </label>
                                    <p className="text-lg text-stone-500 font-mono bg-stone-50 p-2 rounded">
                                        {agent?.agent_id}
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-base font-medium text-stone-400 mb-1">
                                        Organization ID
                                    </label>
                                    <p className="text-lg text-stone-500 font-mono bg-stone-50 p-2 rounded">
                                        {agent?.org_id}
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-base font-medium text-stone-400 mb-1">
                                        Created
                                    </label>
                                    <p className="text-stone-600 text-lg">
                                        {agent?.created_at
                                            ? new Date(
                                                  agent.created_at
                                              ).toLocaleDateString()
                                            : "N/A"}
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-base font-medium text-stone-400 mb-1">
                                        Status
                                    </label>
                                    <p className="text-stone-600 text-lg">
                                        <span
                                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                agent?.active
                                                    ? "bg-green-100 text-green-800"
                                                    : "bg-red-100 text-red-800"
                                            }`}
                                        >
                                            {agent?.active
                                                ? "Active"
                                                : "Inactive"}
                                        </span>
                                    </p>
                                </div>
                                {agent?.resource_urls &&
                                    agent.resource_urls.length > 0 && (
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Resource URLs (
                                                {agent.resource_urls.length})
                                            </label>
                                            <div className="space-y-1">
                                                {agent.resource_urls
                                                    .slice(0, 3)
                                                    .map((url, index) => (
                                                        <div
                                                            key={index}
                                                            className="flex items-center gap-2"
                                                        >
                                                            <a
                                                                href={url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-citrus-500 hover:text-citrus-600 text-xs break-all"
                                                            >
                                                                {url.length > 30
                                                                    ? `${url.substring(
                                                                          0,
                                                                          30
                                                                      )}...`
                                                                    : url}
                                                            </a>
                                                        </div>
                                                    ))}
                                                {agent.resource_urls.length >
                                                    3 && (
                                                    <p className="text-xs text-stone-400">
                                                        +
                                                        {agent.resource_urls
                                                            .length - 3}{" "}
                                                        more
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                {agent?.file_urls &&
                                    agent.file_urls.length > 0 && (
                                        <div>
                                            <label className="block text-base font-medium text-stone-400 mb-1">
                                                Files ({agent.file_urls.length})
                                            </label>
                                            <div className="space-y-1">
                                                {agent.file_urls
                                                    .slice(0, 3)
                                                    .map((fileUrl, index) => (
                                                        <div
                                                            key={index}
                                                            className="flex items-center gap-2"
                                                        >
                                                            <a
                                                                href={fileUrl}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-citrus-500 hover:text-citrus-600 text-xs break-all"
                                                            >
                                                                {fileUrl
                                                                    .split("/")
                                                                    .pop() ||
                                                                    `File ${
                                                                        index +
                                                                        1
                                                                    }`}
                                                            </a>
                                                        </div>
                                                    ))}
                                                {agent.file_urls.length > 3 && (
                                                    <p className="text-xs text-stone-400">
                                                        +
                                                        {agent.file_urls
                                                            .length - 3}{" "}
                                                        more
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    )}
                            </div>
                        </div>

                        {/* Quick Actions */}
                        {!isEditing && (
                            <div className="bg-white py-6 rounded-lg shadow-lg border border-stone-200">
                                <h2 className="text-xl px-6 border-b pb-4 font-semibold text-stone-500 mb-6">
                                    Quick Actions
                                </h2>
                                <div className="flex gap-3 flex-col px-6">
                                    <button
                                        onClick={handleToggleStatus}
                                        className="px-4 py-2 rounded font-medium transition-colors bg-stone-500 hover:bg-stone-600 text-white"
                                    >
                                        Toggle Status
                                    </button>
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="bg-citrus-500 hover:bg-citrus-600 text-white px-4 py-2 rounded font-medium transition-colors"
                                    >
                                        Edit Agent
                                    </button>

                                    <button
                                        onClick={handleDeleteAgent}
                                        className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-medium transition-colors"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
