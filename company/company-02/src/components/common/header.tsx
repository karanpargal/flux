"use client";

import { useState } from "react";

export default function Header() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <header className="relative z-50 w-full border-b border-retro-500/20 bg-dark-950/80 backdrop-blur-md">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 items-center justify-between">
                    {/* Logo */}
                    <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-retro-500 to-cyan-500 flex items-center justify-center">
                            <span className="text-white font-bold text-lg">
                                D
                            </span>
                        </div>
                        <span className="text-xl font-bold animate-neon-glow text-retro-400">
                            DashX
                        </span>
                    </div>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center space-x-8">
                        <a
                            href="#features"
                            className="text-gray-300 hover:text-retro-400 transition-colors duration-300 font-medium"
                        >
                            Features
                        </a>
                        <a
                            href="#documentation"
                            className="text-gray-300 hover:text-retro-400 transition-colors duration-300 font-medium"
                        >
                            Documentation
                        </a>
                        <a
                            href="#pricing"
                            className="text-gray-300 hover:text-retro-400 transition-colors duration-300 font-medium"
                        >
                            Pricing
                        </a>
                    </nav>

                    {/* CTA Buttons */}
                    <div className="hidden md:flex items-center space-x-4">
                        <button className="text-gray-300 hover:text-retro-400 transition-colors duration-300 font-medium">
                            Book a Demo
                        </button>
                        <button className="retro-button">Signup / Login</button>
                    </div>

                    {/* Mobile menu button */}
                    <button
                        className="md:hidden text-gray-300 hover:text-retro-400 transition-colors duration-300"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                    >
                        <svg
                            className="h-6 w-6"
                            fill="none"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            {isMenuOpen ? (
                                <path d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path d="M4 6h16M4 12h16M4 18h16" />
                            )}
                        </svg>
                    </button>
                </div>

                {/* Mobile Navigation */}
                {isMenuOpen && (
                    <div className="md:hidden">
                        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-retro-500/20">
                            <a
                                href="#features"
                                className="block px-3 py-2 text-gray-300 hover:text-retro-400 transition-colors duration-300"
                            >
                                Features
                            </a>
                            <a
                                href="#documentation"
                                className="block px-3 py-2 text-gray-300 hover:text-retro-400 transition-colors duration-300"
                            >
                                Documentation
                            </a>
                            <a
                                href="#pricing"
                                className="block px-3 py-2 text-gray-300 hover:text-retro-400 transition-colors duration-300"
                            >
                                Pricing
                            </a>
                            <div className="px-3 py-2 space-y-2">
                                <button className="block w-full text-left text-gray-300 hover:text-retro-400 transition-colors duration-300">
                                    Book a Demo
                                </button>
                                <button className="retro-button w-full">
                                    Signup / Login
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
}
