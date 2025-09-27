// API Response Types
export type ApiResponse<T> =
    | {
          success: true;
          data: T;
      }
    | {
          success: false;
          message: string;
      };

// Organization Types
export interface Organization {
    org_id: string;
    name: string;
    industry: "Tech";
    multisig_wallet_address: string | null;
    team_size: number;
    email: string | null;
    created_at: string;
}

export interface CreateOrganizationRequest {
    name: string;
    industry: "Tech";
    multisig_wallet_address?: string;
    team_size: number;
    email?: string;
}

export interface UpdateOrganizationRequest {
    name?: string;
    industry?: "Tech";
    multisig_wallet_address?: string;
    team_size?: number;
    email?: string;
}

// Agent Types
export interface Agent {
    agent_id: string;
    name: string;
    description: string | null;
    org_id: string;
    created_at: string;
    active: boolean;
    file_urls: string[];
    resource_urls: string[];
}

export interface CreateAgentRequest {
    name: string;
    description?: string | null;
    org_id: string;
    org_name: string;
    resource_urls?: string[];
    file_urls?: string[];
}

export interface UpdateAgentRequest {
    name?: string;
    description?: string;
    org_id?: string;
}

// API Client Configuration
export interface ApiClientConfig {
    baseUrl: string;
    headers?: Record<string, string>;
}

// Hook States
export interface UseQueryState<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
}

export interface UseMutationState<T, TArgs extends unknown[] = unknown[]> {
    data: T | null;
    loading: boolean;
    error: string | null;
    execute: (...args: TArgs) => Promise<T>;
    reset: () => void;
}
