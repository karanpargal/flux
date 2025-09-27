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
