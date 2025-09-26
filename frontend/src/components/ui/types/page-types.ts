export interface LandingPageProps {
    className?: string;
}

export interface DashboardLayoutProps {
    children: React.ReactNode;
    className?: string;
}

export interface DashboardPageProps {
    className?: string;
}

export interface AgentFormProps {
    onSubmit: (values: AgentFormValues) => void;
    className?: string;
}

export interface AgentCardProps {
    agent: Agent;
    onEdit?: (agent: Agent) => void;
    onDelete?: (agent: Agent) => void;
    onToggleStatus?: (agent: Agent) => void;
    className?: string;
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

export interface AgentFormValues {
    name: string;
    description: string;
    agentType: string;
    capabilities: string;
    context: string;
}
