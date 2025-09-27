"use client";
import LoginForm from "@/components/forms/login-form";
import { LoginFormValues } from "@/components/ui/types/form-types";
import { useRouter } from "next/navigation";
import Marquee from "react-fast-marquee";

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
        <div className="min-h-screen flex flex-col justify-between">
            {/* Top Marquee - Forward Direction */}
            <Marquee
                speed={50}
                direction="left"
                className="bg-gradient-to-r from-blue-500/10 to-orange-500/10 py-4"
            >
                <div className="flex items-center space-x-8 text-sm font-semibold text-gray-600">
                    <span>📈 Document Reference</span>
                    <span>🔧 Transaction Verification</span>
                    <span>🌟 Calculator</span>
                    <span>💡 Refund Processing</span>
                    <span>🎯 Customer Support</span>
                    <span>✨ Product Information</span>
                    <span>🔧 Technical Support</span>
                    <span>🌟 Billing Support</span>
                    <span>💡 General Inquiries</span>
                    <span>🚀 AI-Powered Support</span>
                </div>
            </Marquee>

            <section className="flex items-center justify-center  p-8">
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

            {/* Bottom Marquee - Backward Direction */}
            <Marquee
                speed={50}
                direction="right"
                className="bg-gradient-to-r from-orange-500/10 to-blue-500/10 py-4"
            >
                <div className="flex items-center space-x-8 text-sm font-semibold text-gray-600">
                    <span>📈 Document Reference</span>
                    <span>🔧 Transaction Verification</span>
                    <span>🌟 Calculator</span>
                    <span>💡 Refund Processing</span>
                    <span>🎯 Customer Support</span>
                    <span>✨ Product Information</span>
                    <span>🔧 Technical Support</span>
                    <span>🌟 Billing Support</span>
                    <span>💡 General Inquiries</span>
                    <span>🚀 AI-Powered Support</span>
                </div>
            </Marquee>
        </div>
    );
}
