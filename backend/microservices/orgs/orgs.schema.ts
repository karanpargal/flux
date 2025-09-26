import { evmAddressSchema } from "../../utils/shared.schema";
import { MappedOrg } from "../../utils/types/mappers.types";
import { type PartialYupSchema } from "../../utils/types/shared.types";
import * as yup from "yup";

export const createOrgBody = yup
    .object()
    .shape<PartialYupSchema<MappedOrg>>({
        name: yup.string().trim().required(),
        industry: yup.string().oneOf(["Tech"]).required(),
        multisig_wallet_address: evmAddressSchema,
        team_size: yup.number().integer().min(1).required(),
    })
    .strict()
    .noUnknown()
    .required();

export const updateOrgBody = yup
    .object()
    .shape<PartialYupSchema<MappedOrg>>({
        name: yup.string().trim().optional(),
        industry: yup.string().oneOf(["Tech"]).optional(),
        multisig_wallet_address: evmAddressSchema.optional(),
        team_size: yup.number().integer().min(1).optional(),
    })
    .strict()
    .noUnknown()
    .required();

export const getOrgParams = yup
    .object()
    .shape({
        org_id: yup.string().trim().required(),
    })
    .strict()
    .noUnknown()
    .required();
