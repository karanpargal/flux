import { LoggerService, SupabaseService } from "../../services";
import { SUPABASE_NO_ROWS_ERROR_CODE } from "../../utils/constants";
import { MappedOrg } from "../../utils/types/mappers.types";

const logger = LoggerService.scoped("orgs");

export const createOrg = async ({
    industry,
    name,
    team_size,
    email,
    password,
}: MappedOrg) => {
    const log = logger.scoped("createOrg");

    const { data, error } = await SupabaseService.getSupabase()
        .from("orgs")
        .insert({
            industry,
            name,
            team_size,
            email,
            password,
        })
        .select()
        .single();

    if (error) {
        log.error("create-failed", {
            data: {
                industry,
                name,
                team_size,
                email,
            },
            error,
        });
        throw error;
    }

    log.info("org-created", {
        org_id: data.org_id,
        name: data.name,
    });
    return data;
};

export const getOrgById = async (org_id: string) => {
    const log = logger.scoped("getOrgById");

    const { data, error } = await SupabaseService.getSupabase()
        .from("orgs")
        .select()
        .eq("org_id", org_id)
        .single();

    if (error && error.code !== SUPABASE_NO_ROWS_ERROR_CODE) {
        log.error("query-failed", {
            org_id,
            error,
        });
        throw error;
    }

    return data;
};

export const updateOrg = async (
    org_id: MappedOrg["org_id"],
    { industry, multisig_wallet_address, name, email, team_size }: MappedOrg,
) => {
    const log = logger.scoped("updateOrg");

    const { data, error } = await SupabaseService.getSupabase()
        .from("orgs")
        .update({
            industry,
            multisig_wallet_address,
            name,
            team_size,
            email,
        })
        .eq("org_id", org_id)
        .select()
        .single();

    if (error) {
        log.error("update-failed", {
            org_id,
            data: {
                industry,
                multisig_wallet_address,
                name,
                team_size,
                email,
            },
            error,
        });
        throw error;
    }

    log.info("org-updated", {
        org_id,
        name: data.name,
    });
    return data;
};

export const deleteOrg = async (org_id: MappedOrg["org_id"]) => {
    const log = logger.scoped("deleteOrg");

    const { error } = await SupabaseService.getSupabase()
        .from("orgs")
        .delete()
        .eq("org_id", org_id);

    if (error) {
        log.error("delete-failed", {
            org_id,
            error,
        });
        throw error;
    }

    log.info("org-deleted", {
        org_id,
    });
};

export const loginOrg = async (email: string, password: string) => {
    const log = logger.scoped("loginOrg");

    try {
        const { data, error } = await SupabaseService.getSupabase()
            .from("orgs")
            .select()
            .eq("email", email)
            .eq("password", password)
            .single();

        if (error) {
            throw error;
        }

        log.info("org-login-successful", {
            data,
        });

        return data;
    } catch (error) {
        log.error("login-org-failed", {
            email,
            error,
        });
        throw error;
    }
};
