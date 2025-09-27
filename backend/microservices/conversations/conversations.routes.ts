import { validateQuery } from "../../middlewares";
import { LoggerService } from "../../services";
import { MappedChatMessage } from "../../utils/types/mappers.types";
import { ResponseWithData } from "../../utils/types/shared.types";
import {
    chatCompletionBody,
    getConversationHistoryQuery,
} from "./conversations.schema.js";
import {
    getConversationHistory,
    processChatCompletion,
} from "./conversations.service";
import type { NextFunction, Request, Response } from "express";
import { Router } from "express";

export const conversationsRouter = Router();

const logger = LoggerService.scoped("conversations");

// GET /conversations/history - Get conversation history with filters
const handleGetConversationHistory = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("getConversationHistory");
    try {
        const { user_id, agent_id, org_id } = req.query;

        const data = await log.time("fetch-conversation-history", () =>
            getConversationHistory(
                user_id as string,
                agent_id as string,
                org_id as string,
            ),
        );

        return res.json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedChatMessage[]>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// POST /conversations/chat - Process chat completion
const handleChatCompletion = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("chatCompletion");
    try {
        const { content, user_id, agent_id, org_id } = req.body;

        const result = await log.time("process-chat-completion", () =>
            processChatCompletion({
                content,
                user_id,
                agent_id,
                org_id,
            }),
        );

        return res.json({
            success: true,
            data: result.data,
        });
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// Routes
conversationsRouter.post(
    "/",
    validateQuery("body", chatCompletionBody),
    handleChatCompletion,
);
conversationsRouter.get(
    "/history",
    validateQuery("query", getConversationHistoryQuery),
    handleGetConversationHistory,
);
