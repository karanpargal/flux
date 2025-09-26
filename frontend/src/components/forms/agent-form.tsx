"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import { AgentFormValues } from "../ui/types/form-types";
import { AgentFormProps } from "../ui/types/page-types";

const agentTypes = [
    { value: "customer-support", label: "Customer Support" },
    { value: "technical-support", label: "Technical Support" },
    { value: "sales", label: "Sales" },
    { value: "billing", label: "Billing" },
    { value: "general", label: "General" },
    { value: "escalation", label: "Escalation" },
];

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

const AgentForm: React.FC<AgentFormProps> = ({ onSubmit, className = "" }) => {
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        reset,
    } = useForm<AgentFormValues>({
        resolver: yupResolver(validationSchema),
    });

    const handleFormSubmit = (values: AgentFormValues) => {
        onSubmit(values);
        reset();
    };

    return (
        <div
            className={`bg-white p-8 rounded-lg shadow-lg border border-stone-200 ${className}`}
        >
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-stone-500 mb-2">
                    Create New Agent
                </h2>
                <p className="text-stone-400">
                    Set up a new support agent for your organization
                </p>
            </div>

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
                            errors.name ? "border-red-500" : "border-stone-300"
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

                {/* Submit Button */}
                <div className="flex gap-4">
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="flex-1 bg-citrus-500 hover:bg-citrus-600 disabled:bg-citrus-400 text-white font-medium py-2 px-4 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                    >
                        {isSubmitting ? "Creating Agent..." : "Create Agent"}
                    </button>
                    <button
                        type="button"
                        onClick={() => reset()}
                        className="px-4 py-2 border border-stone-300 text-stone-500 rounded-md hover:bg-stone-50 transition-colors focus:outline-none focus:ring-2 focus:ring-stone-500 focus:ring-offset-2"
                    >
                        Reset
                    </button>
                </div>
            </form>
        </div>
    );
};

export default AgentForm;
