import * as yup from "yup";

export const evmAddressSchema = yup
    .string()
    .trim()
    .matches(/^0x[a-fA-F0-9]{40}$/, "Must be a valid EVM address")
    .test("starts-with-0x", "Must start with 0x", (value) =>
        value ? value.startsWith("0x") : false,
    );
