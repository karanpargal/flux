import { type Database } from "./database.types";

export { Database };
export type MappedOrg = Database["public"]["Tables"]["orgs"]["Row"];
