"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import { AgentFormValues } from "../ui/types/form-types";
import { AgentFormProps } from "../ui/types/page-types";
import { useCreateAgent } from "../../lib/hooks";
import { Agent } from "@/lib/types";

const validationSchema = Yup.object({
  name: Yup.string()
    .min(2, "Agent name must be at least 2 characters")
    .max(50, "Agent name must be less than 50 characters")
    .required("Agent name is required"),
  description: Yup.string().nullable().optional(),
  org_id: Yup.string().required("Organization ID is required"),
  org_name: Yup.string().required("Organization name is required"),
  resource_urls: Yup.array()
    .of(Yup.string().url("Must be a valid URL"))
    .optional(),
  file_urls: Yup.array().of(Yup.string()).optional(),
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
      resource_urls: [],
      file_urls: [],
    },
  });

  const createAgent = useCreateAgent();

  React.useEffect(() => {
    if (orgId) setValue("org_id", orgId);
    if (orgName) setValue("org_name", orgName);
  }, [orgId, orgName, setValue]);

  const handleFormSubmit = async (values: Record<string, unknown>) => {
    try {
      const processedValues = {
        name: values.name as string,
        description: (values.description as string) || null,
        org_id: values.org_id as string,
        org_name: values.org_name as string,
        resource_urls: (values.resource_urls as string[]) || [],
        file_urls: (values.file_urls as string[]) || [],
        capabilities: {}, // Default empty capabilities object
      };

      const newAgent = await createAgent.execute(processedValues);
      onSubmit(values as unknown as AgentFormValues);
      reset();
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

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
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
              errors.description ? "border-red-500" : "border-stone-300"
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
          <textarea
            id="resource_urls"
            rows={3}
            onChange={(e) => {
              const urls = e.target.value
                .split("\n")
                .filter((url) => url.trim() !== "");
              setValue("resource_urls", urls);
            }}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
              errors.resource_urls ? "border-red-500" : "border-stone-300"
            }`}
            placeholder="Enter resource URLs (one per line)&#10;Example:&#10;https://docs.example.com&#10;https://api.example.com/docs"
          />
          <p className="mt-1 text-sm text-stone-400">
            Enter one URL per line. These will be used as knowledge sources for
            the agent.
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
          <input
            type="file"
            id="files"
            multiple
            accept=".pdf"
            onChange={(e) => {
              const files = Array.from(e.target.files || []);
              // For now, we'll store file names as strings
              // In a real implementation, you'd upload these files
              const fileNames = files.map((file) => file.name);
              setValue("file_urls", fileNames);
            }}
            className="w-full px-3 py-2 border border-stone-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500"
          />
          <p className="mt-1 text-sm text-stone-400">
            Upload PDF files that the agent can reference (max 5MB per file, up
            to 10 files)
          </p>
          {errors.file_urls && (
            <div className="mt-1 text-sm text-red-600">
              {errors.file_urls.message}
            </div>
          )}
        </div>

        {createAgent.error && (
          <div className="p-4 border border-red-300 bg-red-50 rounded-md">
            <p className="text-sm text-red-600">{createAgent.error}</p>
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
