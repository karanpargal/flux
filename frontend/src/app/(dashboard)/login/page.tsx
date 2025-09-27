"use client";
import LoginForm from "@/components/forms/login-form";
import { LoginFormValues } from "@/components/ui/types/form-types";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const router = useRouter();

    const handleLogin = (values: LoginFormValues) => {
        console.log("Login form submitted:", values);
        if (values.organizationId) {
            router.push(`/dashboard?orgId=${values.organizationId}`);
        } else {
            router.push("/dashboard");
        }
    };

    return (
        <section className="grid grid-cols-1 lg:grid-cols-2">
            <div className="flex flex-col">
                <h1>Login</h1>
                <p>
                    Welcome back! Sign in to your organization account to
                    continue.
                </p>
            </div>
            <div className="flex justify-center lg:justify-end">
                <div className="w-full max-w-md">
                    <LoginForm onSubmit={handleLogin} />
                </div>
            </div>
        </section>
    );
}
