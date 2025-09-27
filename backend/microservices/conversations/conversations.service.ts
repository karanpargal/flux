import { LoggerService, SupabaseService } from "../../services";
import { TablesInsert } from "../../utils/types/database.types";
import { MappedChatMessage } from "../../utils/types/mappers.types";

const logger = LoggerService.scoped("conversations");

export const createChatMessage = async ({
    content,
    role,
    user_id,
    agent_id,
    org_id,
}: MappedChatMessage) => {
    const log = logger.scoped("createChatMessage");

    const { data, error } = await SupabaseService.getSupabase()
        .from("chat_messages")
        .insert({
            content,
            role,
            user_id,
            agent_id,
            org_id,
        })
        .select()
        .single();

    if (error) {
        log.error("create-failed", {
            data: {
                content,
                role,
                user_id,
                agent_id,
                org_id,
            },
            error,
        });
        throw error;
    }

    log.info("chat-message-created", {
        chat_messages_id: data.chat_messages_id,
        role: data.role,
        user_id: data.user_id,
    });
    return data;
};

export const getConversationHistory = async (
    user_id: string,
    agent_id?: string,
    org_id?: string,
) => {
    const log = logger.scoped("getConversationHistory");

    let query = SupabaseService.getSupabase()
        .from("chat_messages")
        .select()
        .eq("user_id", user_id);

    if (agent_id) {
        query = query.eq("agent_id", agent_id);
    }

    if (org_id) {
        query = query.eq("org_id", org_id);
    }

    const { data, error } = await query.order("created_at", {
        ascending: true,
    });

    if (error) {
        log.error("query-failed", {
            user_id,
            agent_id,
            org_id,
            error,
        });
        throw error;
    }

    return data;
};

export const deleteConversationHistory = async (
    user_id: string,
    agent_id?: string,
    org_id?: string,
) => {
    const log = logger.scoped("deleteConversationHistory");

    let query = SupabaseService.getSupabase()
        .from("chat_messages")
        .delete()
        .eq("user_id", user_id);

    if (agent_id) {
        query = query.eq("agent_id", agent_id);
    }

    if (org_id) {
        query = query.eq("org_id", org_id);
    }

    const { error } = await query;

    if (error) {
        log.error("delete-failed", {
            user_id,
            agent_id,
            org_id,
            error,
        });
        throw error;
    }

    log.info("conversation-history-deleted", {
        user_id,
        agent_id,
        org_id,
    });
};

export const processChatCompletion = async ({
    content,
    user_id,
    agent_id,
    org_id,
}: {
    content: string;
    user_id: string;
    agent_id: string;
    org_id: string;
}) => {
    const log = logger.scoped("processChatCompletion");

    try {
        // 1. Create user message locally (don't store yet)
        const userMessage: TablesInsert<"chat_messages"> = {
            content,
            role: "user",
            user_id,
            agent_id,
            org_id,
            created_at: new Date().toISOString(),
        };

        // 2. Forward to third-party chat completions API (matching Python chat routes structure)
        const thirdPartyUrl = `${process.env.THIRD_PARTY_SERVER_URL}/chat/completions?agent_id=${agent_id}`;

        const chatRequest = {
            messages: [
                {
                    role: "user",
                    content: content,
                },
            ],
            model: "asi1-fast",
            temperature: 0.7,
            max_tokens: 1000,
            stream: false,
        };

        const response = await fetch(thirdPartyUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(chatRequest),
        });

        if (!response.ok) {
            // Try to get the response body for more details about the error
            let errorDetails = null;
            try {
                errorDetails = await response.text();
            } catch (e) {
                errorDetails = "Could not read error response body";
            }
            
            log.error("third-party-api-failed", {
                status: response.status,
                statusText: response.statusText,
                agent_id,
                errorDetails,
                requestUrl: thirdPartyUrl,
                requestBody: chatRequest,
            });
            throw new Error(
                `Third-party API failed: ${response.status} ${response.statusText}. Details: ${errorDetails}`,
            );
        }

        const chatResponse = await response.json();

        // 3. Parse response according to chat routes structure
        log.debug("received-chat-response", {
            response: chatResponse,
            agent_id,
        });

        const choices = chatResponse.choices || [];
        if (choices.length === 0) {
            log.error("no-choices-in-response", {
                response: chatResponse,
                agent_id,
            });
            throw new Error("No choices in chat response");
        }

        const choice = choices[0];
        const assistantContent = choice?.message?.content;
        
        if (!assistantContent || assistantContent.trim() === "") {
            log.error("invalid-assistant-response", {
                response: chatResponse,
                choice: choice,
                agent_id,
                assistantContent,
            });
            throw new Error("Invalid assistant response format - empty or missing content");
        }

        // 4. Create assistant message
        const assistantMessage: TablesInsert<"chat_messages"> = {
            content: assistantContent,
            role: "assistant",
            user_id,
            agent_id,
            org_id,
            created_at: new Date().toISOString(),
        };

        // 5. Bulk insert both messages (fire and forget)
        const messagesToInsert = [userMessage, assistantMessage];

        // Fire and forget - don't wait for the result
        (async () => {
            try {
                const { error } = await SupabaseService.getSupabase()
                    .from("chat_messages")
                    .insert(messagesToInsert);

                if (error) {
                    log.error("bulk-insert-failed", {
                        user_id,
                        agent_id,
                        org_id,
                        error,
                    });
                } else {
                    log.info("messages-stored", {
                        user_id,
                        agent_id,
                        count: messagesToInsert.length,
                    });
                }
            } catch (error: any) {
                log.error("bulk-insert-error", {
                    user_id,
                    agent_id,
                    org_id,
                    error,
                });
            }
        })();

        // 6. Return the assistant message content to client
        return {
            success: true,
            data: {
                content: assistantContent,
                role: "assistant",
                user_id,
                agent_id,
                org_id,
            } as MappedChatMessage,
        };
    } catch (error) {
        log.error("chat-completion-failed", {
            user_id,
            agent_id,
            org_id,
            error,
        });
        throw error;
    }
};
