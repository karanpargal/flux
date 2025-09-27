import { MappedAgent, MappedOrg } from "../../utils/types/mappers.types";
import { type PartialYupSchema } from "../../utils/types/shared.types";
import * as yup from "yup";

export const createAgentBody = yup
    .object()
    .shape<PartialYupSchema<MappedAgent & { org_name: MappedOrg["name"] }>>({
        name: yup.string().trim().required(),
        description: yup.string().trim().nullable().optional(),
        org_id: yup.string().trim().required(),
        org_name: yup.string().trim().required(),
        file_urls: yup.array().of(yup.string().trim()).required(),
        resource_urls: yup.array().of(yup.string().trim()).required(),
    })
    .strict()
    .noUnknown()
    .required();

export const updateAgentBody = yup
    .object()
    .shape<PartialYupSchema<MappedAgent>>({
        name: yup.string().trim().optional(),
        description: yup.string().trim().nullable().optional(),
        org_id: yup.string().trim().optional(),
    })
    .strict()
    .noUnknown()
    .required();

export const getAgentParams = yup
    .object()
    .shape({
        agent_id: yup.string().trim().required(),
    })
    .strict()
    .noUnknown()
    .required();

export const getAgentsForOrgParams = yup
    .object()
    .shape({
        org_id: yup.string().trim().required(),
    })
    .strict()
    .noUnknown()
    .required();

export const uploadFileParams = yup
    .object()
    .shape({
        org_id: yup.string().trim().required(),
        agent_id: yup.string().trim().required(),
    })
    .strict()
    .noUnknown()
    .required();

export const updateActiveStatusBody = yup
    .object()
    .shape({
        active: yup.boolean().required(),
    })
    .strict()
    .noUnknown()
    .required();
