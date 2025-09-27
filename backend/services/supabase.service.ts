import { Database } from "../utils/types/mappers.types";
import { LoggerService } from "./logger.service";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

export class SupabaseService {
    private static logger = LoggerService.scoped("SupabaseService");
    private static anonClient: SupabaseClient<Database>;
    private static adminClient: SupabaseClient<Database>;

    public static initAnon = (): void => {
        this.anonClient = createClient<Database>(
            process.env.SUPABASE_URL as string,
            process.env.SUPABASE_PUBLISHABLE_KEY as string,
        );
    };

    public static initAdmin = (): void => {
        this.adminClient = createClient<Database>(
            process.env.SUPABASE_URL as string,
            process.env.SUPABASE_SECRET_KEY as string,
        );
    };

    public static init = async (): Promise<void> => {
        if (
            !process.env.SUPABASE_URL &&
            !process.env.SUPABASE_PUBLISHABLE_KEY
            // &&
            // !process.env.SUPABASE_SERVICE_ROLE_KEY
        ) {
            this.logger.error("missing-env-variables");
            process.exit(1);
        }

        this.initAnon();
        // this.initAdmin();
        this.logger.info("init-success");
    };

    public static getSupabase = (
        access?: "admin" | string,
    ): SupabaseClient<Database> => {
        if (access === "admin") {
            if (!this.adminClient) {
                this.initAdmin();
            }
            return this.adminClient;
        }

        // if (access) {
        //     return createClient<Database>(
        //         process.env.SUPABASE_URL!,
        //         process.env.SUPABASE_KEY!,
        //         {
        //             global: {
        //                 headers: {
        //                     authorization: `Bearer ${access}`,
        //                 },
        //             },
        //         },
        //     );
        // }

        if (!this.anonClient) {
            this.initAnon();
        }
        return this.anonClient;
    };
}
