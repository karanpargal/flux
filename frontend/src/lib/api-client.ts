import {
    Organization,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    Agent,
    CreateAgentRequest,
    UpdateAgentRequest,
    ApiClientConfig,
} from "./types";

class ApiClient {
    private baseUrl: string;
    private headers: Record<string, string>;

    constructor(config: ApiClientConfig) {
        this.baseUrl = config.baseUrl;
        this.headers = {
            "Content-Type": "application/json",
            ...config.headers,
        };
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;

        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.headers,
                ...options.headers,
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                errorData.message ||
                    `HTTP ${response.status}: ${response.statusText}`
            );
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || "API request failed");
        }

        return data.data;
    }

    // Organization API methods
    async getOrganization(orgId: string): Promise<Organization> {
        return this.request<Organization>(`/api/v1/orgs/${orgId}`);
    }

    async createOrganization(
        data: CreateOrganizationRequest
    ): Promise<Organization> {
        return this.request<Organization>("/api/v1/orgs", {
            method: "POST",
            body: JSON.stringify(data),
        });
    }

    async updateOrganization(
        orgId: string,
        data: UpdateOrganizationRequest
    ): Promise<Organization> {
        return this.request<Organization>(`/api/v1/orgs/${orgId}`, {
            method: "PUT",
            body: JSON.stringify(data),
        });
    }

    async deleteOrganization(orgId: string): Promise<void> {
        await fetch(`${this.baseUrl}/api/v1/orgs/${orgId}`, {
            method: "DELETE",
            headers: this.headers,
        });
    }

    async loginOrganization(
        email: string,
        password: string
    ): Promise<Organization> {
        return this.request<Organization>("/api/v1/orgs/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });
    }

    // Agent API methods
    async getAgent(agentId: string): Promise<Agent> {
        return this.request<Agent>(`/api/v1/agents/${agentId}`);
    }

    async getAgentsForOrg(orgId: string): Promise<Agent[]> {
        return this.request<Agent[]>(`/api/v1/agents/org/${orgId}`);
    }

    async createAgent(data: CreateAgentRequest): Promise<Agent> {
        return this.request<Agent>("/api/v1/agents", {
            method: "POST",
            body: JSON.stringify(data),
        });
    }

    async updateAgent(
        agentId: string,
        data: UpdateAgentRequest
    ): Promise<Agent> {
        return this.request<Agent>(`/api/v1/agents/${agentId}`, {
            method: "PUT",
            body: JSON.stringify(data),
        });
    }

    async deleteAgent(agentId: string): Promise<void> {
        await fetch(`${this.baseUrl}/api/v1/agents/${agentId}`, {
            method: "DELETE",
            headers: this.headers,
        });
    }
}

// Create and export the default API client instance
const apiClient = new ApiClient({
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
});

export { apiClient, ApiClient };
export default apiClient;
