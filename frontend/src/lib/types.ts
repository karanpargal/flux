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
  created_at: string;
  org_id: string;
  name: string;
  industry: "Tech";
  team_size: number;
  multisig_wallet_address: string | null;
  email: string | null;
}

// Agent Types
export interface Agent {
  active: boolean;
  agent_id: string;
  capabilities: Record<string, unknown>;
  // capabilities: {
  //   [tool_name: string]: {
  //     description: string;
  //     parameters: Record<string, unknown>;
  // }[]};
  created_at: string;
  description: string | null;
  file_urls: string[];
  name: string;
  org_id: string;
  resource_urls: string[];
  updated_at: string;
}

// Agent creation request type (without file_urls since backend generates them)
export type CreateAgentRequest = Omit<
  Agent,
  "agent_id" | "created_at" | "updated_at" | "file_urls"
> & {
  org_name: string;
};

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
