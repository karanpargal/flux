import { execSync } from "child_process";
import "dotenv/config";
import { readFileSync, writeFileSync } from "fs";
import { resolve } from "path";
import { format } from "prettier";

(async () => {
    try {
        const SUPABASE_ACCESS_TOKEN = process.env.SUPABASE_ACCESS_TOKEN;
        const SUPABASE_PROJECT_ID = process.env.SUPABASE_PROJECT_ID;

        if (!SUPABASE_ACCESS_TOKEN || !SUPABASE_PROJECT_ID) {
            throw new Error(
                "Error: SUPABASE_ACCESS_TOKEN and SUPABASE_PROJECT_ID must be set in .env file",
            );
        }

        const outFile = "utils/types/database.types.ts";

        execSync(`npx supabase login --token ${SUPABASE_ACCESS_TOKEN}`, {
            stdio: "inherit",
        });

        execSync(
            `npx supabase gen types --lang=typescript --project-id ${SUPABASE_PROJECT_ID} > ${outFile}`,
            { stdio: "inherit" },
        );

        const typesContent = readFileSync(outFile, "utf-8");
        const prettierConfig = JSON.parse(
            readFileSync(resolve(process.cwd(), ".prettierrc"), "utf-8"),
        );
        const formattedContent = await format(typesContent, {
            ...prettierConfig,
            parser: "typescript",
        });
        writeFileSync(outFile, formattedContent);

        console.log("Successfully generated and formatted Supabase types!");
    } catch (error) {
        console.error("Error generating types:", error);
        process.exit(1);
    }
})();
