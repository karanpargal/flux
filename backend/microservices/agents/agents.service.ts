import { LoggerService, SupabaseService } from "../../services";
import { SUPABASE_NO_ROWS_ERROR_CODE } from "../../utils/constants";
import { MappedAgent, MappedOrg } from "../../utils/types/mappers.types";

const logger = LoggerService.scoped("agents");

export const notifyThirdPartyServer = async (
    org_name: MappedOrg["name"],
    {
        description,
        name,
        org_id,
    }: Omit<
        MappedAgent,
        "created_at" | "agent_id" | "active" | "ens" | "wallet_address"
    >,
) => {
    const log = logger.scoped("notifyThirdPartyServer");

    try {
        const thirdPartyUrl =
            process.env.THIRD_PARTY_SERVER_URL ||
            "https://api.example.com/agents";

        const response = await fetch(thirdPartyUrl + "/company-agents", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                description,
                agent_name: name,
                company_id: org_id,
                company_name: org_name,
                capabilities: [],
                pdf_document_urls: [],
                support_categories: [],
                company_products: [],
            }),
        });

        if (!response.ok) {
            throw new Error(
                `Third-party server responded with status: ${response.status}`,
            );
        }

        const { agent_id, address, ens_name } = await response.json();

        log.info("third-party-notification-success", {
            agent_id,
            status: response.status,
        });

        return {
            agent_id,
            address,
            ens_name,
        };
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
    ens,
    wallet_address,
}: Omit<MappedAgent, "created_at">) => {
    const log = logger.scoped("storeAgentInDatabase");

    const { data, error } = await SupabaseService.getSupabase()
        .from("agents")
        .insert({
            name,
            org_id,
            agent_id,
            description,
            ens,
            wallet_address,
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
    files?: any[],
) => {
    const log = logger.scoped("createAgent");

    try {
        const { agent_id, address, ens_name } = await notifyThirdPartyServer(
            org_name,
            {
                capabilities: [],
                file_urls,
                resource_urls,
                name,
                description,
                org_id,
            },
        );

        // If files are provided, upload them during creation
        let finalFileUrls = file_urls || [];
        if (files && files.length > 0) {
            log.info("uploading-files-during-creation", {
                agent_id,
                org_id,
                fileCount: files.length,
            });

            const uploadResults = await uploadFilesToSupabase(
                agent_id,
                org_id,
                files,
                finalFileUrls,
            );
            finalFileUrls = uploadResults.successful.map(
                (result) => result.public_url,
            );

            if (uploadResults.failed.length > 0) {
                log.warn("some-files-failed-during-creation", {
                    agent_id,
                    failedCount: uploadResults.failed.length,
                    failedFiles: uploadResults.failed.map((f) => f.file_name),
                });
            }
        }

        const data = await storeAgentInDatabase({
            capabilities: [],
            active: true,
            file_urls: finalFileUrls,
            resource_urls,
            agent_id,
            name,
            description,
            org_id,
            ens: ens_name,
            wallet_address: address,
        });

        log.info("agent-created-successfully", {
            agent_id: data.agent_id,
            name: data.name,
            fileCount: finalFileUrls.length,
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
    org_id: string,
    file: any,
    currentFileUrls: string[],
) => {
    const log = logger.scoped("uploadFileToSupabase");

    try {
        const file_name = file.originalname;
        const storage_path = `${org_id}/${agent_id}/${file_name}`;

        // Upload file to Supabase Storage with nested path
        const { data, error } = await SupabaseService.getSupabase()
            .storage.from("supportify")
            .upload(storage_path, file.buffer, {
                contentType: file.mimetype,
                cacheControl: "3600",
                upsert: true,
            });

        if (error) {
            log.error("upload-failed", {
                agent_id,
                org_id,
                file_name,
                storage_path,
                error,
            });
            throw error;
        }

        // Get public URL for the uploaded file
        const {
            data: { publicUrl },
        } = SupabaseService.getSupabase()
            .storage.from("supportify")
            .getPublicUrl(storage_path);

        // Update agent's file_urls array with the new file URL
        await updateAgentFileUrls(agent_id, publicUrl, currentFileUrls);

        log.info("file-uploaded-successfully", {
            agent_id,
            org_id,
            file_name,
            storage_path,
            public_url: publicUrl,
        });

        return publicUrl;
    } catch (error) {
        log.error("upload-file-failed", {
            agent_id,
            org_id,
            originalName: file.originalname,
            error,
        });
        throw error;
    }
};

export const uploadFilesToSupabase = async (
    agent_id: string,
    org_id: string,
    files: any[],
    currentFileUrls: string[],
) => {
    const log = logger.scoped("uploadFilesToSupabase");

    const results = {
        successful: [] as { file_name: string; public_url: string }[],
        failed: [] as { file_name: string; error: string }[],
    };

    // Process each file individually
    for (const file of files) {
        try {
            const public_url = await uploadFileToSupabase(
                agent_id,
                org_id,
                file,
                currentFileUrls,
            );
            results.successful.push({
                file_name: file.originalname,
                public_url,
            });

            // Update currentFileUrls for the next file
            currentFileUrls.push(public_url);
        } catch (error) {
            const errorMessage =
                error instanceof Error ? error.message : "Unknown error";
            results.failed.push({
                file_name: file.originalname,
                error: errorMessage,
            });

            log.error("individual-file-upload-failed", {
                agent_id,
                org_id,
                file_name: file.originalname,
                error: errorMessage,
            });
        }
    }

    log.info("batch-upload-completed", {
        agent_id,
        org_id,
        totalFiles: files.length,
        successful: results.successful.length,
        failed: results.failed.length,
    });

    return results;
};

export const deleteUploadedFile = async (
    agent_id: string,
    file_url: string,
) => {
    const log = logger.scoped("deleteUploadedFile");

    try {
        // Get current agent data
        const agent = await getAgentById(agent_id);

        // Remove the file URL from the agent's file_urls array
        const currentFileUrls = agent?.file_urls || [];
        const updatedFileUrls = currentFileUrls.filter(
            (url) => url !== file_url,
        );

        if (currentFileUrls.length === updatedFileUrls.length) {
            log.warn("file-url-not-found", {
                agent_id,
                file_url,
            });
            throw new Error("File URL not found in agent's file list");
        }

        // Extract the file path from the public URL for storage deletion
        // The file URL format is: https://[project].supabase.co/storage/v1/object/public/supportify/[org_id]/[agent_id]/[file_name]
        const urlParts = file_url.split("/");
        const storagePath = urlParts
            .slice(urlParts.indexOf("supportify") + 1)
            .join("/");

        // Delete the file from Supabase storage
        const { error: storageError } = await SupabaseService.getSupabase()
            .storage.from("supportify")
            .remove([storagePath]);

        if (storageError) {
            log.warn("storage-deletion-failed", {
                agent_id,
                file_url,
                storagePath,
                error: storageError,
            });
            // Continue with database update even if storage deletion fails
        } else {
            log.info("file-deleted-from-storage", {
                agent_id,
                file_url,
                storagePath,
            });
        }

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
                file_url,
                error,
            });
            throw error;
        }

        log.info("file-url-removed", {
            agent_id,
            file_url,
            remainingFiles: updatedFileUrls.length,
        });

        return data;
    } catch (error) {
        log.error("delete-uploaded-file-failed", {
            agent_id,
            file_url,
            error,
        });
        throw error;
    }
};

export const removeResourceUrl = async (
    agent_id: string,
    resource_url: string,
) => {
    const log = logger.scoped("removeResourceUrl");

    try {
        // Get current agent data
        const agent = await getAgentById(agent_id);

        // Remove the resource URL from the agent's resource_urls array
        const currentResourceUrls = agent?.resource_urls || [];
        const updatedResourceUrls = currentResourceUrls.filter(
            (url) => url !== resource_url,
        );

        if (currentResourceUrls.length === updatedResourceUrls.length) {
            log.warn("resource-url-not-found", {
                agent_id,
                resource_url,
            });
            throw new Error("Resource URL not found in agent's resource list");
        }

        // Update the agent with the new resource_urls array
        const { data, error } = await SupabaseService.getSupabase()
            .from("agents")
            .update({ resource_urls: updatedResourceUrls })
            .eq("agent_id", agent_id)
            .select()
            .single();

        if (error) {
            log.error("update-resource-urls-failed", {
                agent_id,
                resource_url,
                error,
            });
            throw error;
        }

        log.info("resource-url-removed", {
            agent_id,
            resource_url,
            remainingResources: updatedResourceUrls.length,
        });

        return data;
    } catch (error) {
        log.error("remove-resource-url-failed", {
            agent_id,
            resource_url,
            error,
        });
        throw error;
    }
};

export const addResourceUrls = async (
    agent_id: string,
    newResourceUrls: string[],
) => {
    const log = logger.scoped("addResourceUrls");

    try {
        // Get current agent data
        const agent = await getAgentById(agent_id);

        // Merge new resource URLs with existing ones, avoiding duplicates
        const currentResourceUrls = agent?.resource_urls || [];
        const urlSet = new Set([...currentResourceUrls, ...newResourceUrls]);
        const updatedResourceUrls = Array.from(urlSet);

        // Update the agent with the new resource_urls array
        const { data, error } = await SupabaseService.getSupabase()
            .from("agents")
            .update({ resource_urls: updatedResourceUrls })
            .eq("agent_id", agent_id)
            .select()
            .single();

        if (error) {
            log.error("update-resource-urls-failed", {
                agent_id,
                newResourceUrls,
                error,
            });
            throw error;
        }

        log.info("resource-urls-added", {
            agent_id,
            newResourceUrls,
            totalResources: updatedResourceUrls.length,
        });

        return data;
    } catch (error) {
        log.error("add-resource-urls-failed", {
            agent_id,
            newResourceUrls,
            error,
        });
        throw error;
    }
};
