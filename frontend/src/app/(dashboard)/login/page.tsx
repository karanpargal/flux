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
        <section className="flex items-center justify-center min-h-screen p-8">
            <div className="glass-effect-citrus rounded-3xl p-8 w-full max-w-6xl">
                <div className="grid grid-cols-1 items-start lg:grid-cols-2 gap-8">
                    <div className="flex flex-col gap-y-10">
                        <h1 className="text-5xl font-bold text-gradient-blue-citrus-vertical">
                            Welcome Back
                        </h1>
                        <p className="text-2xl text-stone-500 leading-relaxed">
                            Sign in to your organization account to continue
                            building amazing AI-powered support experiences.
                        </p>
                    </div>
                    <div className="w-full">
                        <LoginForm onSubmit={handleLogin} />
                    </div>
                </div>
            </div>
        </section>
    );
}
