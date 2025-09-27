import { validateQuery } from "../../middlewares";
import { LoggerService } from "../../services";
import { MappedAgent } from "../../utils/types/mappers.types";
import { ResponseWithData } from "../../utils/types/shared.types";
import {
    addResourceUrlsBody,
    addResourceUrlsParams,
    createAgentBody,
    deleteFileParams,
    getAgentParams,
    getAgentsForOrgParams,
    removeResourceParams,
    updateActiveStatusBody,
    updateAgentBody,
    uploadFileParams,
} from "./agents.schema";
import {
    addResourceUrls,
    createAgent,
    deleteAgent,
    deleteUploadedFile,
    getAgentById,
    getAgentsForOrg,
    removeResourceUrl,
    updateAgent,
    updateAgentActiveStatus,
    uploadFilesToSupabase,
} from "./agents.service";
import type { NextFunction, Request, Response } from "express";
import { Router } from "express";
import multer from "multer";

// Extend Request interface to include file property

export const agentsRouter = Router();

const logger = LoggerService.scoped("agents");

const upload = multer({
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 5 * 1024 * 1024, // 5MB limit per file
        files: 10, // Maximum 10 files at once
    },
    fileFilter: (req: any, file: any, cb: any) => {
        const allowedMimes = ["application/pdf"];

        if (allowedMimes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error("File type not allowed"), false);
        }
    },
});

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
        const files = req.files as Express.Multer.File[];

        const data = await log.time("create-agent", () =>
            createAgent(agentData.org_name, agentData, files),
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

// POST /agents/:agent_id/upload - Upload files for agent (supports single or multiple)
const handleUploadFiles = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("uploadFiles");
    try {
        const { org_id, agent_id } = req.params;
        const files = req.files as Express.Multer.File[];
        const { currentFileUrls = [] } = req.body;

        if (!files || files.length === 0) {
            log.error("no-files-provided", {
                agent_id,
            });
            throw new Error("No files provided");
        }

        const results = await log.time("upload-files", () =>
            uploadFilesToSupabase(org_id, files),
        );

        return res.status(201).json({
            success: true,
            data: {
                successful: results.successful,
                failed: results.failed,
                summary: {
                    total: files.length,
                    successful: results.successful.length,
                    failed: results.failed.length,
                },
            },
        } satisfies ResponseWithData<{
            successful: { file_name: string; public_url: string }[];
            failed: { file_name: string; error: string }[];
            summary: {
                total: number;
                successful: number;
                failed: number;
            };
        }>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// PATCH /agents/:agent_id/active - Update agent active status
const handleUpdateActiveStatus = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("updateActiveStatus");
    try {
        const { agent_id } = req.params;
        const { active } = req.body;

        const data = await log.time("update-active-status", () =>
            updateAgentActiveStatus(agent_id, active),
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

// DELETE /agents/:agent_id/files/:file_url - Delete uploaded file
const handleDeleteUploadedFile = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("deleteUploadedFile");
    try {
        const { agent_id, file_url } = req.params;

        const data = await log.time("delete-uploaded-file", () =>
            deleteUploadedFile(agent_id, file_url),
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

// DELETE /agents/:agent_id/resources/:resource_url - Remove resource URL
const handleRemoveResourceUrl = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("removeResourceUrl");
    try {
        const { agent_id, resource_url } = req.params;

        const data = await log.time("remove-resource-url", () =>
            removeResourceUrl(agent_id, resource_url),
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

// POST /agents/:agent_id/resources - Add multiple resource URLs
const handleAddResourceUrls = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("addResourceUrls");
    try {
        const { agent_id } = req.params;
        const { resource_urls } = req.body;

        const data = await log.time("add-resource-urls", () =>
            addResourceUrls(agent_id, resource_urls),
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
    upload.array("files", 3),
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
agentsRouter.post(
    "/:org_id/:agent_id/upload",
    validateQuery("params", uploadFileParams),
    upload.array("files", 3),
    handleUploadFiles,
);
agentsRouter.patch(
    "/:agent_id/active",
    validateQuery("params", getAgentParams),
    validateQuery("body", updateActiveStatusBody),
    handleUpdateActiveStatus,
);
agentsRouter.delete(
    "/:agent_id/files/:file_url",
    validateQuery("params", deleteFileParams),
    handleDeleteUploadedFile,
);
agentsRouter.delete(
    "/:agent_id/resources/:resource_url",
    validateQuery("params", removeResourceParams),
    handleRemoveResourceUrl,
);
agentsRouter.post(
    "/:agent_id/resources",
    validateQuery("params", addResourceUrlsParams),
    validateQuery("body", addResourceUrlsBody),
    handleAddResourceUrls,
);
