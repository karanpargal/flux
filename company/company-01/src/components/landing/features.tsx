"use client";

import { Server, Settings, Shield, Zap, Globe, BarChart3 } from "lucide-react";

export default function Features() {
    const features = [
        {
            icon: Server,
            title: "Hassle-Free Node Deployment",
            description:
                "Streamline your node setup with our seamless deployment process. We handle VPS acquisition and node configuration, so you can focus on your tasks worry-free.",
            color: "from-ocean-500 to-ocean-600",
        },
        {
            icon: Settings,
            title: "Manage All Your Nodes in One Place",
            description:
                "Access all your deployed nodes with ease using our intuitive dashboard. Track node details, manage billing, and access crucial data effortlessly.",
            color: "from-neon-500 to-neon-600",
        },
        {
            icon: Zap,
            title: "Stay Up-to-Date Without the Stress",
            description:
                "Let us handle updates for you. Our automated maintenance feature ensures your nodes stay current, allowing you to focus on your priorities.",
            color: "from-ocean-400 to-neon-400",
        },
        {
            icon: Shield,
            title: "High Grade Servers",
            description:
                "We host all your nodes on high grade servers with 24/7 uptime and enterprise-level security measures.",
            color: "from-neon-400 to-ocean-400",
        },
        {
            icon: Globe,
            title: "Global Infrastructure",
            description:
                "Deploy nodes across multiple regions worldwide for optimal performance and redundancy.",
            color: "from-ocean-500 to-neon-500",
        },
        {
            icon: BarChart3,
            title: "Advanced Analytics",
            description:
                "Monitor your node performance with detailed analytics and real-time monitoring dashboards.",
            color: "from-neon-500 to-ocean-500",
        },
    ];

    return (
        <section id="features" className="py-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        Our Features
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                        Decentralization within reach. Mintair provides a vast
                        selection of chains, ensuring a decentralized blockchain
                        ecosystem.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <div key={index} className="group">
                            <div className="bg-dark-800/50 backdrop-blur-sm border border-ocean-800/30 rounded-2xl p-8 hover:border-ocean-500/50 transition-all duration-300 h-full">
                                <div
                                    className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}
                                >
                                    <feature.icon className="w-8 h-8 text-white" />
                                </div>

                                <h3 className="text-xl font-bold text-white mb-4">
                                    {feature.title}
                                </h3>
                                <p className="text-gray-300 leading-relaxed">
                                    {feature.description}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-16 text-center">
                    <div className="bg-gradient-to-r from-ocean-500/10 to-neon-500/10 border border-ocean-500/20 rounded-2xl p-8">
                        <h3 className="text-2xl font-bold text-white mb-4">
                            Ready to Deploy Your First Node?
                        </h3>
                        <p className="text-gray-300 mb-6">
                            Join thousands of node operators who trust Mintair
                            for their blockchain infrastructure needs.
                        </p>
                        <button className="bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-ocean-600 hover:to-neon-600 transition-all duration-300 transform hover:scale-105">
                            Start Your Journey
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}
