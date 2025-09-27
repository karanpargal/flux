"use client";

import { useState, useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import { AgentFormProps } from "../ui/types/page-types";
import { useCreateAgent } from "../../lib/hooks";
import { Agent } from "@/lib/types";

const AVAILABLE_CAPABILITIES = [
    {
        name: "document_reference",
        displayName: "Document Reference",
        description: "Search and reference company documents, PDFs, and knowledge base",
        configurable: false
    },
    {
        name: "transaction_verification",
        displayName: "Transaction Verification",
        description: "Verify blockchain transactions and payment confirmations",
        configurable: false
    },
    {
        name: "refund_processing",
        displayName: "Refund Processing",
        description: "Process refunds and validate refund requests with company-specific limits",
        configurable: true,
        parameters: [
            {
                name: "max_refund_amount",
                displayName: "Maximum Refund Amount (in wei)",
                type: "string",
                description: "Maximum refund amount allowed in wei (e.g., 1000000000000000000 for 1 ETH)",
                required: false,
                placeholder: "1000000000000000000"
            },
            {
                name: "refund_chain",
                displayName: "Default Refund Chain",
                type: "select",
                description: "Default blockchain network for refunds",
                required: false,
                options: [
                    { value: "ethereum", label: "Ethereum" },
                    { value: "polygon", label: "Polygon" },
                    { value: "bsc", label: "BSC" }
                ],
                default: "ethereum"
            },
            {
                name: "agent_private_key",
                displayName: "Agent Private Key (Encrypted)",
                type: "password",
                description: "Encrypted private key for the agent's wallet to process refunds",
                required: false,
                placeholder: "Enter encrypted private key"
            },
            {
                name: "escalation_threshold",
                displayName: "Escalation Threshold (in wei)",
                type: "string",
                description: "Amount above which refunds require human approval",
                required: false,
                placeholder: "500000000000000000"
            }
        ]
    },
    {
        name: "customer_support",
        displayName: "Customer Support",
        description: "Provide customer support and assistance",
        configurable: false
    },
    {
        name: "product_information",
        displayName: "Product Information",
        description: "Provide information about company products and services",
        configurable: false
    },
    {
        name: "technical_support",
        displayName: "Technical Support",
        description: "Provide technical support and troubleshooting",
        configurable: false
    },
    {
        name: "billing_support",
        displayName: "Billing Support",
        description: "Handle billing inquiries and payment questions",
        configurable: false
    },
    {
        name: "general_inquiries",
        displayName: "General Inquiries",
        description: "Handle general questions and inquiries",
        configurable: false
    }
];

const validationSchema = Yup.object({
    name: Yup.string()
        .min(2, "Agent name must be at least 2 characters")
        .max(50, "Agent name must be less than 50 characters")
        .required("Agent name is required"),
    description: Yup.string().nullable().optional(),
    org_id: Yup.string().required("Organization ID is required"),
    org_name: Yup.string().required("Organization name is required"),
    resource_urls: Yup.string().optional(),
    file_urls: Yup.array().of(Yup.string()).optional(),
    active: Yup.boolean().optional(),
});

const AgentForm: React.FC<AgentFormProps> = ({
    onSubmit,
    onSuccess,
    className = "",
    orgId,
    orgName,
}) => {
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        reset,
        setValue,
    } = useForm({
        resolver: yupResolver(validationSchema),
        defaultValues: {
            name: "",
            description: "",
            org_id: orgId || "",
            org_name: orgName || "",
            resource_urls: "",
            file_urls: [],
            active: true, // Default to active
        },
    });

    const createAgent = useCreateAgent();

    // File upload state
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
    const [dragActive, setDragActive] = useState<boolean>(false);

    // Capabilities state
    const [enabledCapabilities, setEnabledCapabilities] = useState<Set<string>>(new Set());
    const [capabilityConfigs, setCapabilityConfigs] = useState<
        Record<string, Record<string, unknown>>
    >({});

    useEffect(() => {
        if (orgId) setValue("org_id", orgId);
        if (orgName) setValue("org_name", orgName);
    }, [orgId, orgName, setValue]);

    // File handling functions
    const validateFile = (file: File): string | null => {
        if (file.type !== "application/pdf") {
            return "Only PDF files are allowed";
        }
        if (file.size > 5 * 1024 * 1024) {
            return "File size must be less than 5MB";
        }
        return null;
    };

    const handleFiles = useCallback(
        (files: FileList | File[]) => {
            const fileArray = Array.from(files);
            const validFiles: File[] = [];
            const errors: string[] = [];

            fileArray.forEach((file) => {
                const error = validateFile(file);
                if (error) {
                    errors.push(`${file.name}: ${error}`);
                } else {
                    validFiles.push(file);
                }
            });

            if (errors.length > 0) {
                alert(errors.join("\n"));
            }

            const newFiles = [...uploadedFiles, ...validFiles].slice(0, 3); // Max 3 files
            setUploadedFiles(newFiles);
            setValue(
                "file_urls",
                newFiles.map((f) => f.name)
            );
            
            if (newFiles.length > 0 && !enabledCapabilities.has("document_reference")) {
                const newEnabledCapabilities = new Set(enabledCapabilities);
                newEnabledCapabilities.add("document_reference");
                setEnabledCapabilities(newEnabledCapabilities);
            }
        },
        [uploadedFiles, setValue]
    );

    const removeFile = (index: number) => {
        const newFiles = uploadedFiles.filter((_, i) => i !== index);
        setUploadedFiles(newFiles);
        setValue(
            "file_urls",
            newFiles.map((f) => f.name)
        );
        
        if (newFiles.length === 0 && enabledCapabilities.has("document_reference")) {
            const newEnabledCapabilities = new Set(enabledCapabilities);
            newEnabledCapabilities.delete("document_reference");
            setEnabledCapabilities(newEnabledCapabilities);
            const newCapabilityConfigs = { ...capabilityConfigs };
            delete newCapabilityConfigs["document_reference"];
            setCapabilityConfigs(newCapabilityConfigs);
        }
    };

    // Drag and drop handlers
    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            e.stopPropagation();
            setDragActive(false);

            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFiles(e.dataTransfer.files);
            }
        },
        [handleFiles]
    );

    // Capabilities handlers
    const toggleCapability = (capabilityName: string) => {
        const newEnabledCapabilities = new Set(enabledCapabilities);
        if (newEnabledCapabilities.has(capabilityName)) {
            newEnabledCapabilities.delete(capabilityName);
            // Remove capability config when disabled
            const newCapabilityConfigs = { ...capabilityConfigs };
            delete newCapabilityConfigs[capabilityName];
            setCapabilityConfigs(newCapabilityConfigs);
        } else {
            newEnabledCapabilities.add(capabilityName);
        }
        setEnabledCapabilities(newEnabledCapabilities);
    };

    const updateCapabilityConfig = (
        capabilityName: string,
        paramName: string,
        value: unknown
    ) => {
        setCapabilityConfigs((prev) => ({
            ...prev,
            [capabilityName]: {
                ...prev[capabilityName],
                [paramName]: value,
            },
        }));
    };

    const handleFormSubmit = async (values: Record<string, unknown>) => {
        try {
            // Parse comma-separated URLs
            const resourceUrls =
                (values.resource_urls as string)
                    ?.split(",")
                    .map((url) => url.trim())
                    .filter((url) => url.length > 0) || [];

            const processedValues = {
                name: values.name as string,
                description: (values.description as string) || null,
                org_id: values.org_id as string,
                org_name: values.org_name as string,
                resource_urls: resourceUrls,
                file_urls: uploadedFiles.map((f) => f.name),
                active: (values.active as boolean) ?? true,
                capabilities: Object.fromEntries(Array.from(enabledCapabilities).map(capability => [capability, true])), // Send enabled capabilities as array
            };


            const newAgent = await createAgent.execute(processedValues);
            onSubmit(values as unknown as Agent);
            reset();
            setUploadedFiles([]); // Clear uploaded files
            setEnabledCapabilities(new Set()); // Clear capabilities
            setCapabilityConfigs({}); // Clear capability configs
            if (onSuccess) {
                onSuccess(newAgent);
            }
            console.log("Agent created successfully:", newAgent);
        } catch (error) {
            console.error("Failed to create agent:", error);
        }
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

                <input type="hidden" {...register("org_id")} />
                <input type="hidden" {...register("org_name")} />

                {orgName && (
                    <div>
                        <label className="block text-sm font-medium text-stone-500 mb-2">
                            Organization
                        </label>
                        <div className="w-full px-3 py-2 border border-stone-300 rounded-md bg-stone-50 text-stone-600">
                            {orgName}
                        </div>
                    </div>
                )}

                <div>
                    <label
                        htmlFor="description"
                        className="block text-sm font-medium text-stone-500 mb-2"
                    >
                        Description
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
                        placeholder="Describe the agent's role and responsibilities (optional)"
                    />
                    {errors.description && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.description.message}
                        </div>
                    )}
                </div>

                <div>
                    <label
                        htmlFor="resource_urls"
                        className="block text-sm font-medium text-stone-500 mb-2"
                    >
                        Resource URLs
                    </label>
                    <input
                        type="text"
                        id="resource_urls"
                        {...register("resource_urls")}
                        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                            errors.resource_urls
                                ? "border-red-500"
                                : "border-stone-300"
                        }`}
                        placeholder="https://docs.example.com, https://api.example.com/docs"
                    />
                    <p className="mt-1 text-sm text-stone-400">
                        Enter URLs separated by commas. These will be used as
                        knowledge sources for the agent.
                    </p>
                    {errors.resource_urls && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.resource_urls.message}
                        </div>
                    )}
                </div>

                <div>
                    <label
                        htmlFor="files"
                        className="block text-sm font-medium text-stone-500 mb-2"
                    >
                        Upload Files (PDF only)
                    </label>
                    {/* Drag and Drop Area */}
                    <div
                        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                            dragActive
                                ? "border-citrus-500 bg-citrus-50"
                                : "border-stone-300 hover:border-stone-400"
                        }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <input
                            type="file"
                            id="files"
                            multiple
                            accept=".pdf"
                            onChange={(e) => {
                                if (e.target.files) {
                                    handleFiles(e.target.files);
                                }
                            }}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            disabled={uploadedFiles.length >= 3}
                        />

                        <div className="space-y-2">
                            <svg
                                className="mx-auto h-12 w-12 text-stone-400"
                                stroke="currentColor"
                                fill="none"
                                viewBox="0 0 48 48"
                            >
                                <path
                                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                                    strokeWidth={2}
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                            </svg>
                            <div className="text-sm text-stone-600">
                                <span className="font-medium text-citrus-600 hover:text-citrus-500">
                                    Click to upload
                                </span>{" "}
                                or drag and drop
                            </div>
                            <p className="text-xs text-stone-500">
                                PDF files only (max 5MB each, up to 3 files)
                            </p>
                        </div>
                    </div>

                    {/* File List */}
                    {uploadedFiles.length > 0 && (
                        <div className="mt-4 space-y-2">
                            <p className="text-sm font-medium text-stone-500">
                                Uploaded Files:
                            </p>
                            {uploadedFiles.map((file, index) => (
                                <div
                                    key={index}
                                    className="flex items-center justify-between p-3 bg-stone-50 rounded-md border"
                                >
                                    <div className="flex items-center space-x-3">
                                        <svg
                                            className="h-5 w-5 text-red-500"
                                            fill="currentColor"
                                            viewBox="0 0 20 20"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                                                clipRule="evenodd"
                                            />
                                        </svg>
                                        <div>
                                            <p className="text-sm font-medium text-stone-700">
                                                {file.name}
                                            </p>
                                            <p className="text-xs text-stone-500">
                                                {(
                                                    file.size /
                                                    1024 /
                                                    1024
                                                ).toFixed(2)}{" "}
                                                MB
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => removeFile(index)}
                                        className="text-red-500 hover:text-red-700 focus:outline-none focus:text-red-700"
                                    >
                                        <svg
                                            className="h-5 w-5"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M6 18L18 6M6 6l12 12"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                    {errors.file_urls && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.file_urls.message}
                        </div>
                    )}
                </div>

                <div>
                    <label className="flex items-center space-x-3">
                        <input
                            type="checkbox"
                            {...register("active")}
                            className="h-4 w-4 text-citrus-600 focus:ring-citrus-500 border-stone-300 rounded"
                        />
                        <span className="text-sm font-medium text-stone-500">
                            Agent is active
                        </span>
                    </label>
                    <p className="mt-1 text-sm text-stone-400">
                        Active agents can be used for support interactions
                    </p>
                </div>

                {/* Capabilities Section */}
                <div>
                    <label className="block text-sm font-medium text-stone-500 mb-4">
                        Capabilities
                    </label>
                    <p className="text-sm text-stone-400 mb-4">
                        Select and configure tools that this agent can use
                    </p>

                    <div className="space-y-4">
                        {AVAILABLE_CAPABILITIES.map((capability) => (
                            <div
                                key={capability.name}
                                className="border border-stone-200 rounded-lg p-4"
                            >
                                <div className="flex items-start space-x-3">
                                    <input
                                        type="checkbox"
                                        id={`capability-${capability.name}`}
                                        checked={enabledCapabilities.has(capability.name)}
                                        onChange={() => toggleCapability(capability.name)}
                                        disabled={capability.name === "document_reference" && uploadedFiles.length > 0}
                                        className="mt-1 h-4 w-4 text-citrus-600 focus:ring-citrus-500 border-stone-300 rounded disabled:opacity-50"
                                    />
                                    <div className="flex-1">
                                        <label
                                            htmlFor={`capability-${capability.name}`}
                                            className="text-sm font-medium text-stone-700 cursor-pointer"
                                        >
                                            {capability.displayName}
                                            {capability.name === "document_reference" && uploadedFiles.length > 0 && (
                                                <span className="ml-2 text-xs text-citrus-600 bg-citrus-50 px-2 py-1 rounded">
                                                    Auto-enabled (files uploaded)
                                                </span>
                                            )}
                                        </label>
                                        <p className="text-xs text-stone-500 mt-1">
                                            {capability.description}
                                        </p>

                                        {/* Capability Configuration - Only for refund processing */}
                                        {enabledCapabilities.has(capability.name) && capability.configurable && capability.parameters && (
                                            <div className="mt-4 space-y-3">
                                                <p className="text-xs font-medium text-stone-600">
                                                    Configure {capability.displayName} Parameters:
                                                </p>
                                                {capability.parameters.map(
                                                    (param) => (
                                                        <div
                                                            key={param.name}
                                                            className="space-y-1"
                                                        >
                                                            <label className="text-xs font-medium text-stone-500">
                                                                {param.displayName}
                                                                {param.required && <span className="text-red-500 ml-1">*</span>}
                                                            </label>
                                                            <p className="text-xs text-stone-400">
                                                                {param.description}
                                                            </p>

                                                            {param.type === "boolean" ? (
                                                                <div className="flex items-center space-x-2">
                                                                    <input
                                                                        type="checkbox"
                                                                        checked={
                                                                            (capabilityConfigs[
                                                                                capability.name
                                                                            ]?.[
                                                                                param.name
                                                                            ] ??
                                                                                param.default ??
                                                                                false) as boolean
                                                                        }
                                                                        onChange={(
                                                                            e
                                                                        ) =>
                                                                            updateCapabilityConfig(
                                                                                capability.name,
                                                                                param.name,
                                                                                e.target.checked
                                                                            )
                                                                        }
                                                                        className="h-3 w-3 text-citrus-600 focus:ring-citrus-500 border-stone-300 rounded"
                                                                    />
                                                                    <span className="text-xs text-stone-600">
                                                                        {capabilityConfigs[
                                                                            capability.name
                                                                        ]?.[
                                                                            param.name
                                                                        ] ??
                                                                        param.default ??
                                                                        false
                                                                            ? "Yes"
                                                                            : "No"}
                                                                    </span>
                                                                </div>
                                                            ) : param.type === "select" ? (
                                                                <select
                                                                    value={
                                                                        (capabilityConfigs[
                                                                            capability.name
                                                                        ]?.[
                                                                            param.name
                                                                        ] as string) ??
                                                                        param.default ??
                                                                        ""
                                                                    }
                                                                    onChange={(
                                                                        e
                                                                    ) =>
                                                                        updateCapabilityConfig(
                                                                            capability.name,
                                                                            param.name,
                                                                            e.target.value
                                                                        )
                                                                    }
                                                                    className="w-full px-2 py-1 text-xs border border-stone-300 rounded focus:outline-none focus:ring-1 focus:ring-citrus-500 focus:border-citrus-500"
                                                                >
                                                                    <option value="">Select {param.displayName}</option>
                                                                    {param.options?.map((option) => (
                                                                        <option key={option.value} value={option.value}>
                                                                            {option.label}
                                                                        </option>
                                                                    ))}
                                                                </select>
                                                            ) : param.type === "password" ? (
                                                                <input
                                                                    type="password"
                                                                    value={
                                                                        (capabilityConfigs[
                                                                            capability.name
                                                                        ]?.[
                                                                            param.name
                                                                        ] as string) ??
                                                                        ""
                                                                    }
                                                                    onChange={(
                                                                        e
                                                                    ) =>
                                                                        updateCapabilityConfig(
                                                                            capability.name,
                                                                            param.name,
                                                                            e.target.value
                                                                        )
                                                                    }
                                                                    placeholder={param.placeholder || ""}
                                                                    className="w-full px-2 py-1 text-xs border border-stone-300 rounded focus:outline-none focus:ring-1 focus:ring-citrus-500 focus:border-citrus-500"
                                                                />
                                                            ) : (
                                                                <input
                                                                    type="text"
                                                                    value={
                                                                        (capabilityConfigs[
                                                                            capability.name
                                                                        ]?.[
                                                                            param.name
                                                                        ] as string) ??
                                                                        ""
                                                                    }
                                                                    onChange={(
                                                                        e
                                                                    ) =>
                                                                        updateCapabilityConfig(
                                                                            capability.name,
                                                                            param.name,
                                                                            e.target.value
                                                                        )
                                                                    }
                                                                    placeholder={param.placeholder || "Leave empty to use default"}
                                                                    className="w-full px-2 py-1 text-xs border border-stone-300 rounded focus:outline-none focus:ring-1 focus:ring-citrus-500 focus:border-citrus-500"
                                                                />
                                                            )}
                                                        </div>
                                                    )
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {createAgent.error && (
                    <div className="p-4 border border-red-300 bg-red-50 rounded-md">
                        <p className="text-sm text-red-600">
                            {createAgent.error}
                        </p>
                    </div>
                )}

                <div className="flex gap-4">
                    <button
                        type="submit"
                        disabled={isSubmitting || createAgent.loading}
                        className="flex-1 bg-citrus-500 hover:bg-citrus-600 disabled:bg-citrus-400 text-white font-medium py-2 px-4 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                    >
                        {isSubmitting || createAgent.loading
                            ? "Creating Agent..."
                            : "Create Agent"}
                    </button>
                    <button
                        type="button"
                        onClick={() => {
                            reset();
                            setUploadedFiles([]);
                            setEnabledCapabilities(new Set());
                            setCapabilityConfigs({});
                            createAgent.reset();
                        }}
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
