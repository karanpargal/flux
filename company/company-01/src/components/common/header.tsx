"use client";

import { useState } from "react";
import { Menu, X, Zap } from "lucide-react";

export default function Header() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const navigation = [
        { name: "How it works", href: "#how-it-works" },
        { name: "Features", href: "#features" },
        { name: "Chains", href: "#chains" },
        { name: "Community", href: "#community" },
    ];

    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-dark-950/80 backdrop-blur-md border-b border-ocean-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gradient-to-r from-ocean-500 to-neon-500 rounded-lg flex items-center justify-center">
                            <Zap className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold text-white">
                            NodeFlow
                        </span>
                    </div>

                    <nav className="hidden md:flex items-center space-x-8">
                        {navigation.map((item) => (
                            <a
                                key={item.name}
                                href={item.href}
                                className="text-gray-300 hover:text-ocean-400 transition-colors duration-200"
                            >
                                {item.name}
                            </a>
                        ))}
                    </nav>

                    <div className="hidden md:flex items-center space-x-4">
                        <button className="bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-6 py-2 rounded-lg font-medium hover:from-ocean-600 hover:to-neon-600 transition-all duration-200 transform hover:scale-105">
                            Launch App
                        </button>
                    </div>

                    <div className="md:hidden">
                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="text-gray-300 hover:text-white"
                        >
                            {isMenuOpen ? (
                                <X className="w-6 h-6" />
                            ) : (
                                <Menu className="w-6 h-6" />
                            )}
                        </button>
                    </div>
                </div>

                {isMenuOpen && (
                    <div className="md:hidden">
                        <div className="px-2 pt-2 pb-3 space-y-1 bg-dark-900/95 backdrop-blur-md rounded-lg mt-2">
                            {navigation.map((item) => (
                                <a
                                    key={item.name}
                                    href={item.href}
                                    className="block px-3 py-2 text-gray-300 hover:text-ocean-400 transition-colors duration-200"
                                    onClick={() => setIsMenuOpen(false)}
                                >
                                    {item.name}
                                </a>
                            ))}
                            <button className="w-full mt-4 bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-6 py-2 rounded-lg font-medium hover:from-ocean-600 hover:to-neon-600 transition-all duration-200">
                                Launch App
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
}
