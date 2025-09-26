import { type Database } from "./database.types";

export { Database };
export type MappedAgent = Database["public"]["Tables"]["agents"]["Row"];
export type MappedOrg = Database["public"]["Tables"]["orgs"]["Row"];
