import { validateQuery } from "../../middlewares";
import { LoggerService } from "../../services";
import { MappedOrg } from "../../utils/types/mappers.types";
import { ResponseWithData } from "../../utils/types/shared.types";
import {
    createOrgBody,
    getOrgParams,
    loginBody,
    updateOrgBody,
} from "./orgs.schema";
import {
    createOrg,
    deleteOrg,
    getOrgById,
    loginOrg,
    updateOrg,
} from "./orgs.service";
import type { NextFunction, Request, Response } from "express";
import { Router } from "express";

export const orgsRouter = Router();

const logger = LoggerService.scoped("orgs");

// GET /orgs/:org_id - Get organization by ID
const handleGetOrg = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("getOrg");
    try {
        const { org_id } = req.params;

        const data = await log.time("fetch-org", () => getOrgById(org_id));

        if (!data) {
            log.error("org-not-found", {
                org_id,
            });
            throw new Error(`Organization not found for id ${org_id}`);
        }

        return res.json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedOrg>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// POST /orgs - Create new organization
const handleCreateOrg = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("createOrg");
    try {
        const orgData = req.body;

        const data = await log.time("create-org", () => createOrg(orgData));

        return res.status(201).json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedOrg>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// PUT /orgs/:org_id - Update organization
const handleUpdateOrg = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("updateOrg");
    try {
        const { org_id } = req.params;
        const updateData = req.body;

        // Check if organization exists
        const existingOrg = await log.time("check-org-exists", () =>
            getOrgById(org_id),
        );
        if (!existingOrg) {
            log.error("org-not-found", {
                org_id,
            });
            throw new Error(`Organization not found for id ${org_id}`);
        }

        const data = await log.time("update-org", () =>
            updateOrg(org_id, updateData),
        );

        return res.json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedOrg>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// DELETE /orgs/:org_id - Delete organization
const handleDeleteOrg = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("deleteOrg");
    try {
        const { org_id } = req.params;

        // Check if organization exists
        const existingOrg = await log.time("check-org-exists", () =>
            getOrgById(org_id),
        );
        if (!existingOrg) {
            log.error("org-not-found", {
                org_id,
            });
            throw new Error(`Organization not found for id ${org_id}`);
        }

        await log.time("delete-org", () => deleteOrg(org_id));

        return res.status(204).send();
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

// POST /orgs/login - Login organization
const handleLoginOrg = async (
    req: Request,
    res: Response,
    next: NextFunction,
) => {
    const log = logger.scoped("loginOrg");
    try {
        const { email, password } = req.body;

        const data = await log.time("login-org", () =>
            loginOrg(email, password),
        );

        return res.json({
            success: true,
            data,
        } satisfies ResponseWithData<MappedOrg>);
    } catch (error) {
        log.error("request-failed", {
            error,
        });
        next(error);
    }
};

orgsRouter.get("/:org_id", validateQuery("params", getOrgParams), handleGetOrg);
orgsRouter.post("/", validateQuery("body", createOrgBody), handleCreateOrg);
orgsRouter.post("/login", validateQuery("body", loginBody), handleLoginOrg);
orgsRouter.put(
    "/:org_id",
    validateQuery("params", getOrgParams),
    validateQuery("body", updateOrgBody),
    handleUpdateOrg,
);
orgsRouter.delete(
    "/:org_id",
    validateQuery("params", getOrgParams),
    handleDeleteOrg,
);
