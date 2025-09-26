import { LoggerService, SupabaseService } from "../../services";
import { SUPABASE_NO_ROWS_ERROR_CODE } from "../../utils/constants";
import { MappedAgent, MappedOrg } from "../../utils/types/mappers.types";
import { v4 as uuidv4 } from "uuid";

const logger = LoggerService.scoped("agents");

// Send POST request to third-party server
export const notifyThirdPartyServer = async (
    org_name: MappedOrg["name"],
    { agent_id, description, name, org_id }: Omit<MappedAgent, "created_at">,
) => {
    const log = logger.scoped("notifyThirdPartyServer");

    try {
        // Placeholder URL - replace with actual third-party server URL
        const thirdPartyUrl =
            process.env.THIRD_PARTY_SERVER_URL ||
            "https://api.example.com/agents";

        const response = await fetch(thirdPartyUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                agent_id,
                description,
                name,
                org_id,
                org_name,
            }),
        });

        if (!response.ok) {
            throw new Error(
                `Third-party server responded with status: ${response.status}`,
            );
        }

        log.info("third-party-notification-success", {
            agent_id,
            status: response.status,
        });

        return true;
    } catch (error) {
        log.error("third-party-notification-failed", {
            agent_id,
            error,
        });
        throw error;
    }
};

// Store agent in database
export const storeAgentInDatabase = async ({
    agent_id,
    description,
    name,
    org_id,
}: Omit<MappedAgent, "created_at">) => {
    const log = logger.scoped("storeAgentInDatabase");

    const { data, error } = await SupabaseService.getSupabase()
        .from("agents")
        .insert({
            name,
            org_id,
            agent_id,
            description,
        })
        .select()
        .single();

    if (error) {
        log.error("store-failed", {
            data,
            error,
        });
        throw error;
    }

    log.info("agent-stored", {
        agent_id: data.agent_id,
        name: data.name,
    });
    return data;
};

export const createAgent = async (
    org_name: MappedOrg["name"],
    { name, description, org_id }: MappedAgent,
) => {
    const log = logger.scoped("createAgent");

    try {
        const agent_id = uuidv4();

        await notifyThirdPartyServer(org_name, {
            agent_id,
            name,
            description,
            org_id,
        });

        const data = await storeAgentInDatabase({
            agent_id,
            name,
            description,
            org_id,
        });

        log.info("agent-created-successfully", {
            agent_id: data.agent_id,
            name: data.name,
        });

        return data;
    } catch (error) {
        log.error("create-agent-failed", {
            error,
        });
        throw error;
    }
};

export const getAgentById = async (agent_id: string) => {
    const log = logger.scoped("getAgentById");

    const { data, error } = await SupabaseService.getSupabase()
        .from("agents")
        .select()
        .eq("agent_id", agent_id)
        .single();

    if (error && error.code !== SUPABASE_NO_ROWS_ERROR_CODE) {
        log.error("query-failed", {
            agent_id,
            error,
        });
        throw error;
    }

    return data;
};

export const getAgentsForOrg = async (org_id: string) => {
    const log = logger.scoped("getAgentsForOrg");

    const { data, error } = await SupabaseService.getSupabase()
        .from("agents")
        .select()
        .eq("org_id", org_id);

    if (error) {
        log.error("query-failed", {
            org_id,
            error,
        });
        throw error;
    }

    log.info("agents-fetched", {
        org_id,
        count: data.length || 0,
    });
    return data;
};

export const updateAgent = async (
    agent_id: MappedAgent["agent_id"],
    { name, description, org_id }: MappedAgent,
) => {
    const log = logger.scoped("updateAgent");

    const { data, error } = await SupabaseService.getSupabase()
        .from("agents")
        .update({
            name,
            description,
            org_id,
        })
        .eq("agent_id", agent_id)
        .select()
        .single();

    if (error) {
        log.error("update-failed", {
            agent_id,
            data: {
                name,
                description,
                org_id,
            },
            error,
        });
        throw error;
    }

    log.info("agent-updated", {
        agent_id,
        name: data.name,
    });
    return data;
};

export const deleteAgent = async (agent_id: MappedAgent["agent_id"]) => {
    const log = logger.scoped("deleteAgent");

    const { error } = await SupabaseService.getSupabase()
        .from("agents")
        .delete()
        .eq("agent_id", agent_id);

    if (error) {
        log.error("delete-failed", {
            agent_id,
            error,
        });
        throw error;
    }

    log.info("agent-deleted", {
        agent_id,
    });
};
