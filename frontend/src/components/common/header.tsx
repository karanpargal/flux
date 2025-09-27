"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";

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
                        <Image
                            src="/logo.png"
                            alt="Flux"
                            width={80}
                            height={70}
                        />
                        <Link
                            href="/"
                            className="text-3xl font-bold text-stone-500 hover:text-citrus-500 transition-colors -ml-2"
                        >
                            Flux
                        </Link>
                    </div>

                    {/* Navigation */}

                    {/* CTA Button */}
                    <div className="flex items-center space-x-4">
                        <button className=" bg-citrus-600 hover:bg-citrus-700  text-white px-3 py-2 text-base font-medium transition-colors rounded">
                            Sign Out
                        </button>
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
