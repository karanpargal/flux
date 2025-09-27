"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const Header: React.FC = () => {
    const pathname = usePathname();
    return (
        <header
            className={`bg-cream-100/10 shadow-sm border-b border-stone-300`}
        >
            <div className="mx-auto px-4 sm:px-6">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link
                            href="/"
                            className="text-2xl font-bold text-stone-500 hover:text-citrus-500 transition-colors"
                        >
                            Flux
                        </Link>
                    </div>

                    {/* Navigation */}

                    {/* CTA Button */}
                    <div className="flex items-center space-x-4">
                        {pathname === "/dashboard" ? (
                            <button className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors">
                                Sign Out
                            </button>
                        ) : (
                            <>
                                <Link
                                    href="/login"
                                    className="text-stone-400 hover:text-stone-500 px-3 py-2 text-sm font-medium transition-colors"
                                >
                                    Sign In
                                </Link>
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
