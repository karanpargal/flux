"use client";

import { ArrowRight, Play, Zap, Shield, Globe } from "lucide-react";

export default function Hero() {
    return (
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-ocean-950"></div>
            <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%230ea5e9%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%221%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>

            <div className="absolute top-20 left-10 w-20 h-20 bg-ocean-500/20 rounded-full blur-xl animate-float"></div>
            <div
                className="absolute top-40 right-20 w-32 h-32 bg-neon-500/20 rounded-full blur-xl animate-float"
                style={{ animationDelay: "1s" }}
            ></div>
            <div
                className="absolute bottom-40 left-20 w-24 h-24 bg-ocean-400/20 rounded-full blur-xl animate-float"
                style={{ animationDelay: "2s" }}
            ></div>

            <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-ocean-500/10 border border-ocean-500/20 text-ocean-400 text-sm font-medium mb-8">
                    <Zap className="w-4 h-4 mr-2" />
                    One Click Node Deployment
                </div>

                <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                    <span className="block">Blockchain</span>
                    <span className="block bg-gradient-to-r from-ocean-400 to-neon-400 bg-clip-text text-transparent">
                        Infrastructure
                    </span>
                    <span className="block">Made Simple</span>
                </h1>

                <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
                    Deploy blockchain nodes effortlessly in a few clicks, making
                    decentralized networks accessible to everyone. No technical
                    expertise required.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
                    <button className="group bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-ocean-600 hover:to-neon-600 transition-all duration-300 transform hover:scale-105 animate-glow">
                        Deploy Your Node
                        <ArrowRight className="w-5 h-5 ml-2 inline group-hover:translate-x-1 transition-transform" />
                    </button>
                    <button className="group flex items-center px-8 py-4 rounded-xl border border-ocean-500/30 text-ocean-400 hover:bg-ocean-500/10 transition-all duration-300">
                        <Play className="w-5 h-5 mr-2" />
                        Watch Demo
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
                    <div className="text-center">
                        <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                            150,000+
                        </div>
                        <div className="text-gray-400">Node Operators</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                            80,000+
                        </div>
                        <div className="text-gray-400">Nodes Deployed</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                            35+
                        </div>
                        <div className="text-gray-400">Supported Chains</div>
                    </div>
                </div>

                <div className="flex items-center justify-center space-x-8 mt-16">
                    <div className="flex items-center space-x-2 text-gray-400">
                        <Shield className="w-5 h-5" />
                        <span className="text-sm">Secure</span>
                    </div>
                    <div className="flex items-center space-x-2 text-gray-400">
                        <Zap className="w-5 h-5" />
                        <span className="text-sm">Fast</span>
                    </div>
                    <div className="flex items-center space-x-2 text-gray-400">
                        <Globe className="w-5 h-5" />
                        <span className="text-sm">Global</span>
                    </div>
                </div>
            </div>

            <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
                <div className="w-6 h-10 border-2 border-ocean-400 rounded-full flex justify-center">
                    <div className="w-1 h-3 bg-ocean-400 rounded-full mt-2 animate-pulse"></div>
                </div>
            </div>
        </div>
    );
}
