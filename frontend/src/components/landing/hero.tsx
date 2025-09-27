"use client";
import React from "react";
import { LandingPageProps } from "../ui/types/page-types";
import { useRouter } from "next/navigation";
import DitherBackground from "./DitherBackground";

export const Hero: React.FC<LandingPageProps> = ({ className = "" }) => {
    const router = useRouter();
    return (
        <div className={`min-h-screen relative overflow-hidden ${className}`}>
            <DitherBackground variant="vibrant" />
            {/* Subtle overlay for text readability */}
            <div className="absolute inset-0 bg-cream-300/12 z-10"></div>
            {/* Hero Section */}
            <section className="relative z-10 p-24 px-4 sm:px-6 lg:px-20 h-1/2">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Left Column - Content */}
                    <div className="backdrop-blur-3xl  translate-y-1/2 p-10 gap-y-4 flex flex-col items-center rounded h-full">
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gradient-blue-citrus-horizontal leading-tight">
                            Streamline Your
                            <span className=" block">Support Operations</span>
                        </h1>
                        <p className="text-xl text-stone-400 leading-relaxed">
                            lorem ipsum dhughfi jhdbiqhdwqhdb jhbdwqihdiwqhj
                        </p>

                        {/* CTA Buttons */}
<div className="flex items-center gap-x-4">

                        <button
                            onClick={() => router.push("/login")}
                            className="border-2 border-citrus-500 bg-citrus-500 hover:bg-citrus-600 text-white px-8 py-2 rounded font-medium text-lg transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                        >
                           Sign In
                        </button>
                        <button
                            onClick={() => router.push("/signup")}
                            className="border-2 border-citrus-500/80 hover:bg-citrus-600 text-white px-8 py-2 rounded font-medium text-lg transition-colors focus:outline-none focus:ring-2 focus:ring-citrus-500 focus:ring-offset-2"
                        >
                            Get Started
                        </button>

</div>
                       
                    </div>

                    {/* Right Column - Sign Up Form */}
                    {/* <video
                        src="/hero.mp4"
                        autoPlay
                        loop
                        muted
                        className="w-full h-full object-cover"
                    ></video> */}
                </div>
            </section>
        </div>
    );
};
