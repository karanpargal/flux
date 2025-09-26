"use client";
import React from "react";
import { LandingPageProps } from "../ui/types/page-types";
import { useRouter } from "next/navigation";

export const Hero: React.FC<LandingPageProps> = ({ className = "" }) => {
    const router = useRouter();
    return (
        <div className={`min-h-screen bg-cream-50 ${className}`}>
            {/* Hero Section */}
            <section className="py-20 px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Left Column - Content */}
                    <div className="space-y-8">
                        <div className="space-y-4">
                            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-stone-500 leading-tight">
                                Streamline Your
                                <span className="text-citrus-500 block">
                                    Support Operations
                                </span>
                            </h1>
                            <p className="text-xl text-stone-400 leading-relaxed">
                                Supportify helps organizations manage customer
                                support tickets, track issues, and deliver
                                exceptional customer experiences with powerful
                                automation and analytics.
                            </p>
                        </div>

                        {/* Key Features */}
                        <div className="space-y-4">
                            <div className="flex items-center space-x-3">
                                <div className="w-6 h-6 bg-citrus-100 rounded-full flex items-center justify-center">
                                    <svg
                                        className="w-4 h-4 text-citrus-500"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                </div>
                                <span className="text-stone-500">
                                    Automated ticket routing and prioritization
                                </span>
                            </div>
                            <div className="flex items-center space-x-3">
                                <div className="w-6 h-6 bg-citrus-100 rounded-full flex items-center justify-center">
                                    <svg
                                        className="w-4 h-4 text-citrus-500"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                </div>
                                <span className="text-stone-500">
                                    Real-time analytics and reporting
                                </span>
                            </div>
                            <div className="flex items-center space-x-3">
                                <div className="w-6 h-6 bg-citrus-100 rounded-full flex items-center justify-center">
                                    <svg
                                        className="w-4 h-4 text-citrus-500"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                </div>
                                <span className="text-stone-500">
                                    Multi-channel support integration
                                </span>
                            </div>
                        </div>

                        {/* CTA Buttons */}
                        <div className="flex flex-col sm:flex-row gap-4">
                            <button
                                onClick={() => router.push("/signup")}
                                className="bg-citrus-500 hover:bg-citrus-600 text-white px-8 py-3 rounded-lg font-medium text-lg transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                            >
                                Get Started
                            </button>
                        </div>
                    </div>

                    {/* Right Column - Sign Up Form */}
                    <div className="border"></div>
                </div>
            </section>
        </div>
    );
};
