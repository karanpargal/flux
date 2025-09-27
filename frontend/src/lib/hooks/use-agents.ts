"use client";

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api-client";
import {
  Agent,
  CreateAgentRequest,
  UseMutationState,
  UseQueryState,
} from "../types";

// Hook to get a single agent
export function useAgent(agentId: string | null): UseQueryState<Agent> {
  const [state, setState] = useState<UseQueryState<Agent>>({
    data: null,
    loading: false,
    error: null,
    refetch: async () => {},
  });

  const fetchAgent = useCallback(async () => {
    if (!agentId) return;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await apiClient.getAgent(agentId);
      setState((prev) => ({ ...prev, data, loading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : "Failed to fetch agent",
        loading: false,
      }));
    }
  }, [agentId]);

  useEffect(() => {
    if (agentId) {
      fetchAgent();
    }
  }, [agentId, fetchAgent]);

  return {
    ...state,
    refetch: fetchAgent,
  };
}

// Hook to get agents for an organization
export function useAgentsForOrg(orgId: string | null): UseQueryState<Agent[]> {
  const [state, setState] = useState<UseQueryState<Agent[]>>({
    data: null,
    loading: false,
    error: null,
    refetch: async () => {},
  });

  const fetchAgents = useCallback(async () => {
    if (!orgId) return;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await apiClient.getAgentsForOrg(orgId);
      setState((prev) => ({ ...prev, data, loading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error:
          error instanceof Error ? error.message : "Failed to fetch agents",
        loading: false,
      }));
    }
  }, [orgId]);

  useEffect(() => {
    if (orgId) {
      fetchAgents();
    }
  }, [orgId, fetchAgents]);

  return {
    ...state,
    refetch: fetchAgents,
  };
}

// Hook to create an agent
export function useCreateAgent(): UseMutationState<
  Agent,
  [CreateAgentRequest, File[]?]
> {
  const [state, setState] = useState<
    UseMutationState<Agent, [CreateAgentRequest, File[]?]>
  >({
    data: null,
    loading: false,
    error: null,
    execute: async () => ({} as Agent),
    reset: () => {},
  });

  const execute = useCallback(
    async (data: CreateAgentRequest, files?: File[]): Promise<Agent> => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const result = await apiClient.createAgent(data, files);
        setState((prev) => ({ ...prev, data: result, loading: false }));
        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Failed to create agent";
        setState((prev) => ({
          ...prev,
          error: errorMessage,
          loading: false,
        }));
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      execute,
      reset: () => {},
    });
  }, [execute]);

  return {
    ...state,
    execute,
    reset,
  };
}

// Hook to update an agent
export function useUpdateAgent(): UseMutationState<
  Agent,
  [string, Partial<Agent>]
> {
  const [state, setState] = useState<
    UseMutationState<Agent, [string, Partial<Agent>]>
  >({
    data: null,
    loading: false,
    error: null,
    execute: async () => ({} as Agent),
    reset: () => {},
  });

  const execute = useCallback(
    async (agentId: string, data: Partial<Agent>): Promise<Agent> => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const result = await apiClient.updateAgent(agentId, data);
        setState((prev) => ({ ...prev, data: result, loading: false }));
        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Failed to update agent";
        setState((prev) => ({
          ...prev,
          error: errorMessage,
          loading: false,
        }));
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      execute,
      reset: () => {},
    });
  }, [execute]);

  return {
    ...state,
    execute,
    reset,
  };
}

// Hook to update agent active status
export function useUpdateAgentStatus(): UseMutationState<
  Agent,
  [string, boolean]
> {
  const [state, setState] = useState<
    UseMutationState<Agent, [string, boolean]>
  >({
    data: null,
    loading: false,
    error: null,
    execute: async () => ({} as Agent),
    reset: () => {},
  });

  const execute = useCallback(
    async (agentId: string, active: boolean): Promise<Agent> => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const result = await apiClient.updateAgentActiveStatus(agentId, active);
        setState((prev) => ({ ...prev, data: result, loading: false }));
        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Failed to update agent status";
        setState((prev) => ({
          ...prev,
          error: errorMessage,
          loading: false,
        }));
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      execute,
      reset: () => {},
    });
  }, [execute]);

  return {
    ...state,
    execute,
    reset,
  };
}

// Hook to delete an agent
export function useDeleteAgent(): UseMutationState<void, [string]> {
  const [state, setState] = useState<UseMutationState<void, [string]>>({
    data: null,
    loading: false,
    error: null,
    execute: async () => {},
    reset: () => {},
  });

  const execute = useCallback(async (agentId: string): Promise<void> => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      await apiClient.deleteAgent(agentId);
      setState((prev) => ({ ...prev, data: null, loading: false }));
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to delete agent";
      setState((prev) => ({
        ...prev,
        error: errorMessage,
        loading: false,
      }));
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      execute,
      reset: () => {},
    });
  }, [execute]);

  return {
    ...state,
    execute,
    reset,
  };
}
