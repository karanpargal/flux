// Re-export API types for consistency
export type {
    Agent,
    Organization,
    CreateAgentRequest,
    CreateOrganizationRequest,
} from "../../../lib/types";

export interface SignUpFormValues {
    organizationName: string;
    email: string;
    password: string;
    organizationType: string;
    organizationId?: string;
}

export interface SignUpFormProps {
    onSubmit: (values: SignUpFormValues) => void;
    className?: string;
}

export interface LoginFormValues {
    email: string;
    password: string;
    organizationId?: string;
}

export interface LoginFormProps {
    onSubmit: (values: LoginFormValues) => void;
    className?: string;
}

export interface AgentFormValues {
    name: string;
    description: string | null;
    org_id: string;
    org_name: string;
    resource_urls: string[];
    file_urls: string[];
}

export interface LegacyAgent {
    id: string;
    name: string;
    description: string;
    agentType: string;
    capabilities: string;
    context: string;
    status: "active" | "inactive";
    createdAt: string;
    updatedAt: string;
    queriesSolved?: number;
}
