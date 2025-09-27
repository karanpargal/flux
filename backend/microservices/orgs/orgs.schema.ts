import { MappedOrg } from "../../utils/types/mappers.types";
import { type PartialYupSchema } from "../../utils/types/shared.types";
import * as yup from "yup";

export const createOrgBody = yup
    .object()
    .shape<PartialYupSchema<MappedOrg>>({
        name: yup.string().trim().required(),
        industry: yup.string().oneOf(["Tech"]).required(),
        multisig_wallet_address: yup.string().nullable(),
        team_size: yup.number().integer().min(1).required(),
        email: yup.string().email().nullable(),
        password: yup.string().required(),
    })
    .strict()
    .noUnknown()
    .required();

export const updateOrgBody = yup
    .object()
    .shape<PartialYupSchema<MappedOrg>>({
        name: yup.string().trim().required(),
        industry: yup.string().oneOf(["Tech"]).required(),
        multisig_wallet_address: yup.string().nullable(),
        team_size: yup.number().integer().min(1).required(),
        email: yup.string().email().nullable().required(),
    })
    .strict()
    .noUnknown()
    .required();

export const getOrgParams = yup
    .object()
    .shape({
        org_id: yup.string().uuid().required(),
    })
    .strict()
    .noUnknown()
    .required();

export const loginBody = yup
    .object()
    .shape({
        email: yup.string().email().required(),
        password: yup.string().required(),
    })
    .strict()
    .noUnknown()
    .required();
