import * as yup from "yup";

export const getConversationHistoryQuery = yup
    .object()
    .shape({
        user_id: yup.string().required(),
        agent_id: yup.string().optional(),
        org_id: yup.string().optional(),
    })
    .strict()
    .noUnknown()
    .required();

export const deleteConversationHistoryQuery = yup
    .object()
    .shape({
        user_id: yup.string().required(),
        agent_id: yup.string().optional(),
        org_id: yup.string().optional(),
    })
    .strict()
    .noUnknown()
    .required();

export const chatCompletionBody = yup
    .object()
    .shape({
        content: yup.string().trim().required(),
        user_id: yup.string().required(),
        agent_id: yup.string().required(),
        org_id: yup.string().required(),
    })
    .strict()
    .noUnknown()
    .required();
