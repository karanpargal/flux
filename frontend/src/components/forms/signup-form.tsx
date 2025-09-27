"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as Yup from "yup";
import { SignUpFormProps, SignUpFormValues } from "../ui/types/form-types";
import { useCreateOrganization } from "../../lib/hooks";

const organizationTypes = [
    { value: "startup", label: "Startup" },
    { value: "small-business", label: "Small Business" },
    { value: "enterprise", label: "Enterprise" },
    { value: "non-profit", label: "Non-Profit" },
    { value: "education", label: "Education" },
    { value: "other", label: "Other" },
];

const validationSchema = Yup.object({
    organizationName: Yup.string()
        .min(2, "Organization name must be at least 2 characters")
        .max(100, "Organization name must be less than 100 characters")
        .required("Organization name is required"),
    email: Yup.string()
        .email("Invalid email address")
        .required("Email is required"),
    password: Yup.string()
        .min(8, "Password must be at least 8 characters")
        .matches(
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
            "Password must contain at least one uppercase letter, one lowercase letter, and one number"
        )
        .required("Password is required"),
    organizationType: Yup.string().required("Organization type is required"),
});

const SignUpForm: React.FC<SignUpFormProps> = ({
    onSubmit,
    className = "",
}) => {
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<SignUpFormValues>({
        resolver: yupResolver(validationSchema),
    });

    const createOrganization = useCreateOrganization();

    const handleFormSubmit = async (values: SignUpFormValues) => {
        try {
            // Create organization with the form data
            const orgData = {
                name: values.organizationName,
                industry: "Tech" as const,
                team_size: 1, // Default team size
                email: values.email,
                password: values.password,
                multisig_wallet_address: null, // Default empty wallet address
            };

            const newOrg = await createOrganization.execute(orgData);

            onSubmit({
                ...values,
                organizationId: newOrg.org_id,
            });
        } catch (error) {
            console.error("Failed to create organization:", error);
        }
    };

    return (
        <div className={`bg-cream-100 p-8 rounded-lg shadow-lg ${className}`}>
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-stone-500 mb-2">
                    Get Started
                </h2>
                <p className="text-stone-400">
                    Create your organization account
                </p>
            </div>

            <form
                onSubmit={handleSubmit(handleFormSubmit)}
                className="space-y-6"
            >
                {/* Organization Name */}
                <div>
                    <label
                        htmlFor="organizationName"
                        className="block text-sm font-medium text-stone-500 mb-2"
                    >
                        Organization Name *
                    </label>
                    <input
                        type="text"
                        id="organizationName"
                        {...register("organizationName")}
                        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                            errors.organizationName
                                ? "border-red-500"
                                : "border-stone-300"
                        }`}
                        placeholder="Enter your organization name"
                    />
                    {errors.organizationName && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.organizationName.message}
                        </div>
                    )}
                </div>

                {/* Email */}
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

                {/* Password */}
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
                        placeholder="Create a strong password"
                    />
                    {errors.password && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.password.message}
                        </div>
                    )}
                </div>

                {/* Organization Type */}
                <div>
                    <label
                        htmlFor="organizationType"
                        className="block text-sm font-medium text-stone-500 mb-2"
                    >
                        Organization Type *
                    </label>
                    <select
                        id="organizationType"
                        {...register("organizationType")}
                        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:border-citrus-500 ${
                            errors.organizationType
                                ? "border-red-500"
                                : "border-stone-300"
                        }`}
                    >
                        <option value="">Select organization type</option>
                        {organizationTypes.map((type) => (
                            <option key={type.value} value={type.value}>
                                {type.label}
                            </option>
                        ))}
                    </select>
                    {errors.organizationType && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors.organizationType.message}
                        </div>
                    )}
                </div>

                {/* Error Display */}
                {createOrganization.error && (
                    <div className="p-4 border border-red-300 bg-red-50 rounded-md">
                        <p className="text-sm text-red-600">
                            {createOrganization.error}
                        </p>
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isSubmitting || createOrganization.loading}
                    className="w-full bg-citrus-500 hover:bg-citrus-600 disabled:bg-citrus-400 text-white font-medium py-2 px-4 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                >
                    {isSubmitting || createOrganization.loading
                        ? "Creating Account..."
                        : "Create Account"}
                </button>

                {/* Terms and Privacy */}
                <div className="flex flex-col gap-y-2">
                    {" "}
                    <p className="text-xs text-stone-400 text-center">
                        Already have an account?{" "}
                        <a
                            href="/login"
                            className="text-citrus-500 underline hover:text-citrus-600"
                        >
                            Login
                        </a>
                    </p>
                    <p className="text-xs text-stone-400 text-center">
                        By creating an account, you agree to our{" "}
                        <a
                            href="#"
                            className="text-citrus-500 hover:text-citrus-600"
                        >
                            Terms of Service
                        </a>{" "}
                        and{" "}
                        <a
                            href="#"
                            className="text-citrus-500 hover:text-citrus-600"
                        >
                            Privacy Policy
                        </a>
                    </p>
                </div>
            </form>
        </div>
    );
};

export default SignUpForm;
