export interface SignUpFormValues {
    organizationName: string;
    email: string;
    password: string;
    organizationType: string;
}

export interface SignUpFormProps {
    onSubmit: (values: SignUpFormValues) => void;
    className?: string;
}

export interface AgentFormValues {
    name: string;
    description: string;
    agentType: string;
    capabilities: string;
    context: string;
}

export interface Agent {
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
