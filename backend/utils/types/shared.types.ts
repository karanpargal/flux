import { type Schema } from "yup";

export type PartialYupSchema<T> = {
    [K in keyof T]?: Schema;
};

export type ResponseWithData<T> =
    | {
          success: true;
          data: T;
      }
    | {
          success: false;
          message: string;
      };
