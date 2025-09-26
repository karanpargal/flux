"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const Header: React.FC = () => {
    const pathname = usePathname();
    return (
        <header className={`bg-cream-100 shadow-sm border-b border-stone-300`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link
                            href="/"
                            className="text-2xl font-bold text-stone-500 hover:text-citrus-500 transition-colors"
                        >
                            Supportify
                        </Link>
                    </div>

                    {/* Navigation */}
                    <nav className="hidden md:flex space-x-8">
                        {pathname === "/dashboard" ? (
                            <Link
                                href="/"
                                className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors"
                            >
                                Home
                            </Link>
                        ) : (
                            <>
                                <a
                                    href="#features"
                                    className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors"
                                >
                                    Features
                                </a>
                                <a
                                    href="#pricing"
                                    className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors"
                                >
                                    Pricing
                                </a>
                                <a
                                    href="#about"
                                    className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors"
                                >
                                    About
                                </a>
                                <a
                                    href="#contact"
                                    className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors"
                                >
                                    Contact
                                </a>
                            </>
                        )}
                    </nav>

                    {/* CTA Button */}
                    <div className="flex items-center space-x-4">
                        {pathname === "/dashboard" ? (
                            <button className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors">
                                Sign Out
                            </button>
                        ) : (
                            <>
                                <button className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors">
                                    Sign In
                                </button>
                                <Link
                                    href="/signup"
                                    className="bg-citrus-500 hover:bg-citrus-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                                >
                                    Get Started
                                </Link>
                            </>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden">
                        <button
                            type="button"
                            className="text-stone-400 hover:text-stone-500 focus:outline-none focus:text-stone-500"
                            aria-label="Open menu"
                        >
                            <svg
                                className="h-6 w-6"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M4 6h16M4 12h16M4 18h16"
                                />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
