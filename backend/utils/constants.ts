import type { CorsOptions } from "cors";
import "dotenv/config";

export const SUPABASE_NO_ROWS_ERROR_CODE = "PGRST116";
export const SUPABASE_UNIQUE_VIOLATION_ERROR_CODE = "23505";

export const CORS_CONFIG = (): CorsOptions => {
    const origins: (string | RegExp)[] = [];

    // Always allow production URL
    origins.push("https://supportify.vercel.app");

    // Development and local environments
    if (process.env.NODE_ENV !== "production") {
        origins.push("http://localhost:3000");
        origins.push("http://127.0.0.1:3000");
        origins.push(/^https:\/\/.*\.ngrok\.io$/); // Support ngrok tunnels
        origins.push(/^https:\/\/.*\.ngrok-free\.app$/); // Support new ngrok domains
        origins.push(/^https:\/\/.*\.ngrok\.app$/); // Support other ngrok variations
    }

    return {
        origin: origins,
        credentials: true,
        methods: ["GET", "POST", "OPTIONS"],
        allowedHeaders: [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            ...(process.env.NODE_ENV !== "production"
                ? ["ngrok-skip-browser-warning"]
                : []),
        ],
        exposedHeaders: ["Content-Length", "X-Foo", "X-Bar"],
        preflightContinue: false,
        optionsSuccessStatus: 200,
    };
};
