"use client";
import SignUpForm from "@/components/forms/signup-form";
import { SignUpFormValues } from "@/components/ui/types/form-types";
import { useRouter } from "next/navigation";

export default function SignupPage() {
    const router = useRouter();

    const handleSignUp = (values: SignUpFormValues) => {
        console.log("Sign up form submitted:", values);
        // TODO: Implement actual sign up logic
        // For now, redirect to dashboard after successful signup
        router.push("/dashboard");
    };
    return (
        <section className="grid grid-cols-1 lg:grid-cols-2">
            <div className="flex flex-col">
                <h1>Signup</h1>
                <p>
                    Lorem ipsum dolor sit amet consectetur adipisicing elit.
                    Quisquam, quos.
                </p>
            </div>
            <div className="flex justify-center lg:justify-end">
                <div className="w-full max-w-md">
                    <SignUpForm onSubmit={handleSignUp} />
                </div>
            </div>
        </section>
    );
}
