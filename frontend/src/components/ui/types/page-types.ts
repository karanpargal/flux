import { Agent } from "@/lib/types";

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
    onSubmit: (values: Agent) => void;
    onSuccess?: (agent: unknown) => void;
    className?: string;
    orgId?: string;
    orgName?: string;
}

export interface AgentCardProps {
    agent: Agent;
    className?: string;
}
