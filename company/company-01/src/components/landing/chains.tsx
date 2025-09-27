"use client";

import { useState } from "react";

export default function Chains() {
    const [selectedChain, setSelectedChain] = useState(0);

    const chains = [
        {
            name: "Ethereum",
            color: "from-blue-500 to-blue-600",
            status: "Live",
        },
        {
            name: "Polygon",
            color: "from-purple-500 to-purple-600",
            status: "Live",
        },
        {
            name: "Solana",
            color: "from-green-500 to-green-600",
            status: "Live",
        },
        { name: "Avalanche", color: "from-red-500 to-red-600", status: "Live" },
        {
            name: "Arbitrum",
            color: "from-blue-400 to-blue-500",
            status: "Live",
        },
        { name: "Optimism", color: "from-red-400 to-red-500", status: "Live" },
        { name: "Base", color: "from-blue-300 to-blue-400", status: "Live" },
        { name: "Linea", color: "from-cyan-500 to-cyan-600", status: "Live" },
        {
            name: "Fuel",
            color: "from-yellow-500 to-yellow-600",
            status: "Live",
        },
        { name: "Taiko", color: "from-pink-500 to-pink-600", status: "Live" },
        {
            name: "Shardeum",
            color: "from-indigo-500 to-indigo-600",
            status: "Live",
        },
        {
            name: "Zora",
            color: "from-orange-500 to-orange-600",
            status: "Live",
        },
    ];

    return (
        <section id="chains" className="py-20 bg-dark-900/50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        Chains Live
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
                        Diverse blockchain network integrations. Discover
                        NodeFlow's wide range of chains, making the blockchain
                        open and decentralized.
                    </p>

                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
                        <div className="text-center">
                            <div className="text-3xl font-bold text-ocean-400 mb-2">
                                150,000+
                            </div>
                            <div className="text-gray-400">Node Operators</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-neon-400 mb-2">
                                80,000+
                            </div>
                            <div className="text-gray-400">Nodes Deployed</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-ocean-400 mb-2">
                                35+
                            </div>
                            <div className="text-gray-400">
                                Affiliated Chains
                            </div>
                        </div>
                    </div>
                </div>

                {/* Chains Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-16">
                    {chains.map((chain, index) => (
                        <div
                            key={index}
                            className={`relative group cursor-pointer transition-all duration-300 ${
                                selectedChain === index
                                    ? "scale-105"
                                    : "hover:scale-105"
                            }`}
                            onClick={() => setSelectedChain(index)}
                        >
                            <div
                                className={`bg-gradient-to-r ${
                                    chain.color
                                } rounded-xl p-6 text-center hover:shadow-lg hover:shadow-${
                                    chain.color.split("-")[1]
                                }-500/25 transition-all duration-300`}
                            >
                                <div className="text-white font-bold text-sm mb-2">
                                    {chain.name}
                                </div>
                                <div className="text-xs text-white/80 bg-white/20 rounded-full px-2 py-1 inline-block">
                                    {chain.status}
                                </div>
                            </div>

                            {/* Selection Indicator */}
                            {selectedChain === index && (
                                <div className="absolute -top-2 -right-2 w-6 h-6 bg-neon-500 rounded-full flex items-center justify-center">
                                    <div className="w-2 h-2 bg-white rounded-full"></div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Selected Chain Info */}
                <div className="bg-dark-800/50 backdrop-blur-sm border border-ocean-800/30 rounded-2xl p-8">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-2xl font-bold text-white">
                            {chains[selectedChain].name} Node
                        </h3>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-neon-500 rounded-full animate-pulse"></div>
                            <span className="text-neon-400 text-sm font-medium">
                                Live
                            </span>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div>
                            <h4 className="text-lg font-semibold text-white mb-4">
                                Node Specifications
                            </h4>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">CPU</span>
                                    <span className="text-white">8 vCPU</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">RAM</span>
                                    <span className="text-white">32 GB</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">
                                        Storage
                                    </span>
                                    <span className="text-white">1 TB SSD</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">
                                        Bandwidth
                                    </span>
                                    <span className="text-white">
                                        Unlimited
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h4 className="text-lg font-semibold text-white mb-4">
                                Pricing
                            </h4>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">
                                        Monthly
                                    </span>
                                    <span className="text-white">
                                        $99/month
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">
                                        Setup Fee
                                    </span>
                                    <span className="text-white">Free</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">
                                        Support
                                    </span>
                                    <span className="text-white">24/7</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">
                                        Uptime SLA
                                    </span>
                                    <span className="text-white">99.9%</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 flex flex-col sm:flex-row gap-4">
                        <button className="flex-1 bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-ocean-600 hover:to-neon-600 transition-all duration-300">
                            Deploy {chains[selectedChain].name} Node
                        </button>
                        <button className="flex-1 border border-ocean-500/30 text-ocean-400 px-6 py-3 rounded-lg font-semibold hover:bg-ocean-500/10 transition-all duration-300">
                            Learn More
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}
