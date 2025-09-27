"use client";

import { useState, useEffect, useCallback } from "react";
import { apiClient } from "../api-client";
import {
    Organization,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    UseQueryState,
    UseMutationState,
} from "../types";

// Hook to get a single organization
export function useOrganization(
    orgId: string | null
): UseQueryState<Organization> {
    const [state, setState] = useState<UseQueryState<Organization>>({
        data: null,
        loading: false,
        error: null,
        refetch: async () => {},
    });

    const fetchOrganization = useCallback(async () => {
        if (!orgId) return;

        setState((prev) => ({ ...prev, loading: true, error: null }));

        try {
            const data = await apiClient.getOrganization(orgId);
            setState((prev) => ({ ...prev, data, loading: false }));
        } catch (error) {
            setState((prev) => ({
                ...prev,
                error:
                    error instanceof Error
                        ? error.message
                        : "Failed to fetch organization",
                loading: false,
            }));
        }
    }, [orgId]);

    useEffect(() => {
        if (orgId) {
            fetchOrganization();
        }
    }, [orgId, fetchOrganization]);

    return {
        ...state,
        refetch: fetchOrganization,
    };
}

// Hook to create an organization
export function useCreateOrganization(): UseMutationState<Organization> {
    const [state, setState] = useState<UseMutationState<Organization>>({
        data: null,
        loading: false,
        error: null,
        execute: async () => ({} as Organization),
        reset: () => {},
    });

    const execute = useCallback(
        async (data: CreateOrganizationRequest): Promise<Organization> => {
            setState((prev) => ({ ...prev, loading: true, error: null }));

            try {
                const result = await apiClient.createOrganization(data);
                setState((prev) => ({ ...prev, data: result, loading: false }));
                return result;
            } catch (error) {
                const errorMessage =
                    error instanceof Error
                        ? error.message
                        : "Failed to create organization";
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

// Hook to update an organization
export function useUpdateOrganization(): UseMutationState<Organization> {
    const [state, setState] = useState<UseMutationState<Organization>>({
        data: null,
        loading: false,
        error: null,
        execute: async () => ({} as Organization),
        reset: () => {},
    });

    const execute = useCallback(
        async (
            orgId: string,
            data: UpdateOrganizationRequest
        ): Promise<Organization> => {
            setState((prev) => ({ ...prev, loading: true, error: null }));

            try {
                const result = await apiClient.updateOrganization(orgId, data);
                setState((prev) => ({ ...prev, data: result, loading: false }));
                return result;
            } catch (error) {
                const errorMessage =
                    error instanceof Error
                        ? error.message
                        : "Failed to update organization";
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

// Hook to delete an organization
export function useDeleteOrganization(): UseMutationState<void> {
    const [state, setState] = useState<UseMutationState<void>>({
        data: null,
        loading: false,
        error: null,
        execute: async () => {},
        reset: () => {},
    });

    const execute = useCallback(async (orgId: string): Promise<void> => {
        setState((prev) => ({ ...prev, loading: true, error: null }));

        try {
            await apiClient.deleteOrganization(orgId);
            setState((prev) => ({ ...prev, data: null, loading: false }));
        } catch (error) {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : "Failed to delete organization";
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

// Hook to login an organization
export function useLoginOrganization(): UseMutationState<Organization> {
    const [state, setState] = useState<UseMutationState<Organization>>({
        data: null,
        loading: false,
        error: null,
        execute: async () => ({} as Organization),
        reset: () => {},
    });

    const execute = useCallback(
        async (email: string, password: string): Promise<Organization> => {
            setState((prev) => ({ ...prev, loading: true, error: null }));

            try {
                const result = await apiClient.loginOrganization(
                    email,
                    password
                );
                setState((prev) => ({ ...prev, data: result, loading: false }));
                return result;
            } catch (error) {
                const errorMessage =
                    error instanceof Error
                        ? error.message
                        : "Failed to login organization";
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
