import { agentsRouter } from "./microservices/agents/agents.routes";
import { conversationsRouter } from "./microservices/conversations/conversations.routes";
import { orgsRouter } from "./microservices/orgs/orgs.routes";
import { LoggerService, SupabaseService } from "./services";
import cors from "cors";
import "dotenv/config";
import type { Express, NextFunction, Request, Response } from "express";
import express, { Router } from "express";
import { createServer } from "node:http";

const app: Express = express();
const server = createServer(app);

app.use(cors());
app.use(express.json());

app.get("/healthcheck", (_req: Request, res: Response) => {
    const now = new Date();
    res.json({
        success: true,
        timestamp: now.toISOString(),
        uptime: process.uptime(),
    });
});

const v1Router = Router();
app.use("/api/v1", v1Router);

v1Router.use("/agents", agentsRouter);
v1Router.use("/conversations", conversationsRouter);
v1Router.use("/orgs", orgsRouter);

app.use("/*splat", (_req: Request, res: Response) => {
    res.status(404).json({
        success: false,
        message: "Not Found",
    });
});

app.use(
    (err: Error | any, _req: Request, res: Response, _next: NextFunction) => {
        const now: Date = new Date();
        const _code = err.errorCode || err.error_code || err.code;
        const code: number =
            typeof _code === "number" && !isNaN(_code) ? _code : 500;
        const message: string =
            err.reason ||
            err.error_message ||
            err.message ||
            "Internal Server Error";
        console.error("[SERVER ERROR]", now.toLocaleString(), err);
        res.status(code).json({
            success: false,
            message,
        });
    },
);

(async () => {
    const log = LoggerService.scoped("server");
    try {
        await Promise.all([SupabaseService.init()]);
        const env: string = process.env.NODE_ENV || "development";
        if (env !== "test") {
            const port: number = +(process.env.PORT || 7990);
            server.listen(port, () => {
                log.info("listening", { port, env });
            });
        }
    } catch (error) {
        log.error("fatal-startup-error", { error });
        process.exit(1);
    }
})();

process.on("SIGINT", () => {
    process.exit(0);
});
process.on("SIGHUP", () => {
    process.exit(0);
});

export default app;
