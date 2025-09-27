"use client";

import { MousePointer, CreditCard, Zap } from "lucide-react";

export default function HowItWorks() {
    const steps = [
        {
            icon: MousePointer,
            title: "Select",
            description:
                "Choose your blockchain node from our extensive list of supported networks.",
            color: "from-ocean-500 to-ocean-600",
        },
        {
            icon: CreditCard,
            title: "Purchase",
            description:
                "Flexible subscription plans tailored to your needs and budget.",
            color: "from-neon-500 to-neon-600",
        },
        {
            icon: Zap,
            title: "Deploy",
            description:
                "Run your node effortlessly with our automated deployment system.",
            color: "from-ocean-400 to-neon-400",
        },
    ];

    return (
        <section id="how-it-works" className="py-20 bg-dark-900/50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        How it works
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                        Simple, Fast, Effortless. Leave behind all the
                        complexities of setting up a node, and become a core
                        contributor of blockchain in a few clicks.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {steps.map((step, index) => (
                        <div key={index} className="relative">
                            {index < steps.length - 1 && (
                                <div className="hidden md:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-ocean-500/50 to-transparent transform translate-x-4"></div>
                            )}

                            <div className="relative bg-dark-800/50 backdrop-blur-sm border border-ocean-800/30 rounded-2xl p-8 hover:border-ocean-500/50 transition-all duration-300 group">
                                <div className="absolute -top-4 -left-4 w-8 h-8 bg-gradient-to-r from-ocean-500 to-neon-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                                    {index + 1}
                                </div>

                                <div
                                    className={`w-16 h-16 bg-gradient-to-r ${step.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}
                                >
                                    <step.icon className="w-8 h-8 text-white" />
                                </div>

                                <h3 className="text-2xl font-bold text-white mb-4">
                                    {step.title}
                                </h3>
                                <p className="text-gray-300 leading-relaxed">
                                    {step.description}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="text-center mt-16">
                    <button className="bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-ocean-600 hover:to-neon-600 transition-all duration-300 transform hover:scale-105">
                        Get Started Now
                    </button>
                </div>
            </div>
        </section>
    );
}
