type LogLevel = "debug" | "info" | "warn" | "error";

type LogMeta = Record<string, unknown> | undefined;

type LogColors = {
    debug: string;
    info: string;
    warn: string;
    error: string;
    reset: string;
};

type ScopedTimer = {
    end: (extraMeta?: LogMeta) => void;
};

 type ScopedLogger = {
    debug: (message: string, meta?: LogMeta) => void;
    info: (message: string, meta?: LogMeta) => void;
    warn: (message: string, meta?: LogMeta) => void;
    error: (message: string, meta?: LogMeta) => void;
    start: (action: string, meta?: LogMeta) => ScopedTimer;
    time: <T>(
        action: string,
        fn: () => Promise<T> | T,
        meta?: LogMeta,
    ) => Promise<T>;
    scoped: (childScope: string, meta?: LogMeta) => ScopedLogger;
};

/**
 * Minimal, dependency-free logger with scopes and high-resolution timings.
 * Output format is single-line JSON for easy ingestion by log platforms.
 */
export class LoggerService {
    private static colors: LogColors = {
        debug: "\x1b[36m", // Cyan
        info: "\x1b[32m", // Green
        warn: "\x1b[33m", // Yellow
        error: "\x1b[31m", // Red
        reset: "\x1b[0m", // Reset
    };

    private static isColorEnabled(): boolean {
        // Default: enable colors in development, disable in production
        return process.env.NODE_ENV !== "production";
    }

    private static isLogLevelEnabled(level: LogLevel): boolean {
        const envLevels = process.env.LOG_LEVEL;
        if (!envLevels) {
            // Default: show all levels
            return true;
        }

        const enabledLevels = envLevels
            .toLowerCase()
            .split(",")
            .map((l) => l.trim());
        return enabledLevels.includes(level);
    }

    private static write(
        level: LogLevel,
        scope: string | undefined,
        message: string,
        meta?: LogMeta,
    ): void {
        // Skip logging if level is not enabled
        if (!this.isLogLevelEnabled(level)) {
            return;
        }

        const ts = new Date().toISOString();
        const levelStr = level.toUpperCase();
        const scopeStr = scope ? ` (${scope})` : "";

        const colorEnabled = this.isColorEnabled();
        const color = colorEnabled ? this.colors[level] : "";
        const reset = colorEnabled ? this.colors.reset : "";

        const line = `${color}${levelStr} [${ts}]${scopeStr} -> ${message}${reset}`;
        const args = meta ? [line, meta] : [line];

        switch (level) {
            case "debug":
                console.debug(...args);
                break;
            case "info":
                console.info(...args);
                break;
            case "warn":
                console.warn(...args);
                break;
            case "error":
                console.error(...args);
                break;
        }
    }

    public static scoped(scope: string, defaultMeta?: LogMeta): ScopedLogger {
        const write = (level: LogLevel, message: string, meta?: LogMeta) =>
            LoggerService.write(
                level,
                scope,
                message,
                meta ? { ...defaultMeta, ...meta } : defaultMeta,
            );

        const start = (action: string, meta?: LogMeta): ScopedTimer => {
            const startNs = process.hrtime.bigint();
            write("debug", `start:${action}` as string, meta);
            return {
                end: (extraMeta?: LogMeta) => {
                    const endNs = process.hrtime.bigint();
                    const durationMs = Number(endNs - startNs) / 1_000_000;
                    write("info", `end:${action}`, {
                        duration_ms: durationMs,
                        ...meta,
                        ...extraMeta,
                    });
                },
            };
        };

        const time = async <T>(
            action: string,
            fn: () => Promise<T> | T,
            meta?: LogMeta,
        ): Promise<T> => {
            const t = start(action, meta);
            try {
                const result = await fn();
                t.end();
                return result;
            } catch (error) {
                t.end({ error });
                throw error;
            }
        };

        const scoped = (childScope: string, meta?: LogMeta): ScopedLogger => {
            const combinedScope = `${scope}::${childScope}`;
            const mergedMeta = meta ? { ...defaultMeta, ...meta } : defaultMeta;
            return LoggerService.scoped(combinedScope, mergedMeta);
        };

        return {
            debug: (message: string, meta?: LogMeta) =>
                write("debug", message, meta),
            info: (message: string, meta?: LogMeta) =>
                write("info", message, meta),
            warn: (message: string, meta?: LogMeta) =>
                write("warn", message, meta),
            error: (message: string, meta?: LogMeta) =>
                write("error", message, meta),
            start,
            time,
            scoped,
        };
    }

    // Root logger without scope
    public static debug(message: string, meta?: LogMeta): void {
        this.write("debug", undefined, message, meta);
    }
    public static info(message: string, meta?: LogMeta): void {
        this.write("info", undefined, message, meta);
    }
    public static warn(message: string, meta?: LogMeta): void {
        this.write("warn", undefined, message, meta);
    }
    public static error(message: string, meta?: LogMeta): void {
        this.write("error", undefined, message, meta);
    }
}
