import type { NextFunction, Request, Response } from "express";
import { Router } from "express";
import { validateQuery } from "../../middlewares";
import { LoggerService } from "../../services";
import { MappedAgent } from "../../utils/types/mappers.types";
import { ResponseWithData } from "../../utils/types/shared.types";
import {
    createAgentBody,
    getAgentParams,
    getAgentsForOrgParams,
    updateAgentBody,
} from "./agents.schema";
import {
    createAgent,
    deleteAgent,
    getAgentById,
    getAgentsForOrg,
    updateAgent,
} from "./agents.service";

export const agentsRouter = Router();

const logger = LoggerService.scoped("agents");

// GET /agents/:agent_id - Get agent by ID
const handleGetAgent = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("getAgent");
    try {
        const { agent_id } = req.params;

        const data = await log.time("fetch-agent", () =>
            getAgentById(agent_id),
        );

        if (!data) {
            log.error("agent-not-found", {
                agent_id,
            });
            throw new Error(`Agent not found for id ${agent_id}`);
        }

        return res.json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedAgent>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// GET /agents/org/:org_id - Get all agents for organization
const handleGetAgentsForOrg = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("getAgentsForOrg");
    try {
        const { org_id } = req.params;

        const data = await log.time("fetch-agents-for-org", () =>
            getAgentsForOrg(org_id),
        );

        return res.json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedAgent[]>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// POST /agents - Create new agent
const handleCreateAgent = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("createAgent");
    try {
        const agentData = req.body;

        const data = await log.time("create-agent", () =>
            createAgent(agentData),
        );

        return res.status(201).json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedAgent>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// PUT /agents/:agent_id - Update agent
const handleUpdateAgent = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("updateAgent");
    try {
        const { agent_id } = req.params;
        const updateData = req.body;

        // Check if agent exists
        const existingAgent = await log.time("check-agent-exists", () =>
            getAgentById(agent_id),
        );
        if (!existingAgent) {
            log.error("agent-not-found", {
                agent_id,
            });
            throw new Error(`Agent not found for id ${agent_id}`);
        }

        const data = await log.time("update-agent", () =>
            updateAgent(agent_id, updateData),
        );

        return res.json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedAgent>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// DELETE /agents/:agent_id - Delete agent
const handleDeleteAgent = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("deleteAgent");
    try {
        const { agent_id } = req.params;

        // Check if agent exists
        const existingAgent = await log.time("check-agent-exists", () =>
            getAgentById(agent_id),
        );
        if (!existingAgent) {
            log.error("agent-not-found", {
                agent_id,
            });
            throw new Error(`Agent not found for id ${agent_id}`);
        }

        await log.time("delete-agent", () => deleteAgent(agent_id));

        return res.status(204).send();
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

agentsRouter.get(
    "/:agent_id",
    validateQuery("params", getAgentParams),
    handleGetAgent,
);
agentsRouter.get(
    "/org/:org_id",
    validateQuery("params", getAgentsForOrgParams),
    handleGetAgentsForOrg,
);
agentsRouter.post(
    "/",
    validateQuery("body", createAgentBody),
    handleCreateAgent,
);
agentsRouter.put(
    "/:agent_id",
    validateQuery("params", getAgentParams),
    validateQuery("body", updateAgentBody),
    handleUpdateAgent,
);
agentsRouter.delete(
    "/:agent_id",
    validateQuery("params", getAgentParams),
    handleDeleteAgent,
);
