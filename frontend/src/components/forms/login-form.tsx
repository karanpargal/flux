"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import { LoginFormProps, LoginFormValues } from "../ui/types/form-types";
import { useLoginOrganization } from "../../lib/hooks";

const validationSchema = Yup.object({
    email: Yup.string()
        .email("Invalid email address")
        .required("Email is required"),
    password: Yup.string()
        .min(8, "Password must be at least 8 characters")
        .required("Password is required"),
});

const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, className = "" }) => {
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<LoginFormValues>({
        resolver: yupResolver(validationSchema),
    });

    const loginOrganization = useLoginOrganization();

    const handleFormSubmit = async (values: LoginFormValues) => {
        try {
            const orgData = await loginOrganization.execute(
                values.email,
                values.password
            );

            onSubmit({
                ...values,
                organizationId: orgData.org_id,
            });
        } catch (error) {
            console.error("Failed to login organization:", error);
        }
    };

    return (
        <div className={`bg-cream-100 p-8 rounded-lg shadow-lg ${className}`}>
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-stone-500 mb-2">
                    Welcome Back
                </h2>
                <p className="text-stone-400">
                    Sign in to your organization account
                </p>
            </div>

            <form
                onSubmit={handleSubmit(handleFormSubmit)}
                className="space-y-6"
            >
                <div>
                    <label
                        htmlFor="email"
                        className="block text-sm font-medium text-stone-500 mb-2"
                    >
                        Email Address *
                    </label>
                    <input
                        type="email"
                        id="email"
                        {...register("email")}
                        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                            errors.email ? "border-red-500" : "border-stone-300"
                        }`}
                        placeholder="Enter your email address"
                    />
                    {errors.email && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.email.message}
                        </div>
                    )}
                </div>

                <div>
                    <label
                        htmlFor="password"
                        className="block text-sm font-medium text-stone-500 mb-2"
                    >
                        Password *
                    </label>
                    <input
                        type="password"
                        id="password"
                        {...register("password")}
                        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                            errors.password
                                ? "border-red-500"
                                : "border-stone-300"
                        }`}
                        placeholder="Enter your password"
                    />
                    {errors.password && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.password.message}
                        </div>
                    )}
                </div>

                {loginOrganization.error && (
                    <div className="p-4 border border-red-300 bg-red-50 rounded-md">
                        <p className="text-sm text-red-600">
                            {loginOrganization.error}
                        </p>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isSubmitting || loginOrganization.loading}
                    className="w-full bg-citrus-500 hover:bg-citrus-600 disabled:bg-citrus-400 text-white font-medium py-2 px-4 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                >
                    {isSubmitting || loginOrganization.loading
                        ? "Signing In..."
                        : "Sign In"}
                </button>

                <div className="flex flex-col gap-y-2">
                    <a
                        href="#"
                        className="text-sm text-center text-citrus-500 hover:text-citrus-600"
                    >
                        Forgot your password?
                    </a>
                    <div className="text-center">
                        <p className="text-sm text-stone-400">
                            Don&apos;t have an account?{" "}
                            <a
                                href="/signup"
                                className="text-citrus-500 underline hover:text-citrus-600 font-medium"
                            >
                                Sign up here
                            </a>
                        </p>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default LoginForm;
