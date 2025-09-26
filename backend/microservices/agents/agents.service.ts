import { LoggerService, SupabaseService } from "../../services";
import { SUPABASE_NO_ROWS_ERROR_CODE } from "../../utils/constants";
import { MappedAgent, MappedOrg } from "../../utils/types/mappers.types";

const logger = LoggerService.scoped("agents");

// Send POST request to third-party server
export const notifyThirdPartyServer = async (
    org_name: MappedOrg["name"],
    {
        description,
        name,
        org_id,
    }: Omit<MappedAgent, "created_at" | "agent_id" | "active">,
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

        const { agent_id } = await response.json();

        log.info("third-party-notification-success", {
            agent_id,
            status: response.status,
        });

        return agent_id;
    } catch (error) {
        log.error("third-party-notification-failed", {
            name,
            org_id,
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
    { name, description, org_id, resource_urls, file_urls }: MappedAgent,
) => {
    const log = logger.scoped("createAgent");

    try {
        const agent_id = await notifyThirdPartyServer(org_name, {
            file_urls,
            resource_urls,
            name,
            description,
            org_id,
        });

        const data = await storeAgentInDatabase({
            active: true,
            file_urls,
            resource_urls,
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

export const updateAgentFileUrls = async (
    agent_id: string,
    fileUrl: string,
    currentFileUrls: string[],
) => {
    const log = logger.scoped("updateAgentFileUrls");

    try {
        // Use Set to avoid duplicates and add the new file URL
        const urlSet = new Set([...currentFileUrls, fileUrl]);
        const updatedFileUrls = Array.from(urlSet);

        // Update the agent with the new file_urls array
        const { data, error } = await SupabaseService.getSupabase()
            .from("agents")
            .update({ file_urls: updatedFileUrls })
            .eq("agent_id", agent_id)
            .select()
            .single();

        if (error) {
            log.error("update-file-urls-failed", {
                agent_id,
                fileUrl,
                error,
            });
            throw error;
        }

        log.info("file-urls-updated", {
            agent_id,
            fileUrl,
            totalFiles: updatedFileUrls.length,
        });

        return data;
    } catch (error) {
        log.error("update-agent-file-urls-failed", {
            agent_id,
            fileUrl,
            error,
        });
        throw error;
    }
};

export const updateAgentActiveStatus = async (
    agent_id: string,
    active: boolean,
) => {
    const log = logger.scoped("updateAgentActiveStatus");

    try {
        // Update the agent with the new active status
        const { data, error } = await SupabaseService.getSupabase()
            .from("agents")
            .update({ active })
            .eq("agent_id", agent_id)
            .select()
            .single();

        if (error) {
            log.error("update-active-status-failed", {
                agent_id,
                active,
                error,
            });
            throw error;
        }

        log.info("agent-active-status-updated", {
            agent_id,
            newStatus: active,
        });

        return data;
    } catch (error) {
        log.error("update-agent-active-status-failed", {
            agent_id,
            error,
        });
        throw error;
    }
};

export const uploadFileToSupabase = async (
    agent_id: string,
    file: any,
    currentFileUrls: string[],
) => {
    const log = logger.scoped("uploadFileToSupabase");

    try {
        const file_name = file.originalname;

        // Upload file to Supabase Storage
        const { data, error } = await SupabaseService.getSupabase()
            .storage.from("supportify")
            .upload(file_name, file.buffer, {
                contentType: file.mimetype,
                cacheControl: "3600",
                upsert: true,
            });

        if (error) {
            log.error("upload-failed", {
                agent_id,
                file_name,
                error,
            });
            throw error;
        }

        // Get public URL for the uploaded file
        const {
            data: { publicUrl },
        } = SupabaseService.getSupabase()
            .storage.from("supportify")
            .getPublicUrl(file_name);

        // Update agent's file_urls array with the new file URL
        await updateAgentFileUrls(agent_id, publicUrl, currentFileUrls);

        log.info("file-uploaded-successfully", {
            agent_id,
            file_name,
            public_url: publicUrl,
        });

        return publicUrl;
    } catch (error) {
        log.error("upload-file-failed", {
            agent_id,
            originalName: file.originalname,
            error,
        });
        throw error;
    }
};
