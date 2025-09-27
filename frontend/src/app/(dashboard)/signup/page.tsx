"use client";
import SignUpForm from "@/components/forms/signup-form";
import { SignUpFormValues } from "@/components/ui/types/form-types";
import { useRouter } from "next/navigation";

export default function SignupPage() {
    const router = useRouter();

    const handleSignUp = (values: SignUpFormValues) => {
        console.log("Sign up form submitted:", values);
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
                            Welcome to Supportify
                        </h1>
                        <p className="text-2xl text-stone-500 leading-relaxed">
                            Create your account and start building amazing
                            AI-powered support experiences for your customers.
                        </p>
                    </div>
                    <div className="w-full">
                        <SignUpForm onSubmit={handleSignUp} />
                    </div>
                </div>
            </div>
        </section>
    );
}
