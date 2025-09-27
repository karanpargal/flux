"use client";

import { Zap, MessageCircle, Twitter, Users, Mail } from "lucide-react";

export default function Footer() {
    const footerLinks = {
        Information: [
            { name: "Dashboard", href: "#" },
            { name: "Documentation", href: "#" },
            { name: "API Reference", href: "#" },
            { name: "Status Page", href: "#" },
        ],
        Company: [
            { name: "About Us", href: "#" },
            { name: "Careers", href: "#" },
            { name: "Press Kit", href: "#" },
            { name: "Contact", href: "#" },
        ],
        Legal: [
            { name: "Terms of Service", href: "#" },
            { name: "Privacy Policy", href: "#" },
            { name: "Cookie Policy", href: "#" },
            { name: "GDPR", href: "#" },
        ],
        Support: [
            { name: "Help Center", href: "#" },
            { name: "Community", href: "#" },
            { name: "Bug Reports", href: "#" },
            { name: "Feature Requests", href: "#" },
        ],
    };

    const socialLinks = [
        { icon: MessageCircle, href: "#", name: "Telegram" },
        { icon: Twitter, href: "#", name: "Twitter" },
        { icon: Users, href: "#", name: "Discord" },
        { icon: Mail, href: "#", name: "Email" },
    ];

    return (
        <footer className="bg-dark-950 border-t border-ocean-800/30">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8 mb-12">
                    <div className="lg:col-span-2">
                        <div className="flex items-center space-x-2 mb-6">
                            <div className="w-8 h-8 bg-gradient-to-r from-ocean-500 to-neon-500 rounded-lg flex items-center justify-center">
                                <Zap className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold text-white">
                                Mintair
                            </span>
                        </div>
                        <p className="text-gray-300 mb-6 max-w-sm">
                            Mintair streamlines the complex process of node
                            running in just a few clicks. Making blockchain
                            infrastructure accessible to everyone.
                        </p>

                        <div className="flex space-x-4">
                            {socialLinks.map((social, index) => (
                                <a
                                    key={index}
                                    href={social.href}
                                    className="w-10 h-10 bg-dark-800 rounded-lg flex items-center justify-center text-gray-400 hover:text-ocean-400 hover:bg-ocean-500/10 transition-all duration-300"
                                    aria-label={social.name}
                                >
                                    <social.icon className="w-5 h-5" />
                                </a>
                            ))}
                        </div>
                    </div>

                    {Object.entries(footerLinks).map(([category, links]) => (
                        <div key={category}>
                            <h3 className="text-white font-semibold mb-4">
                                {category}
                            </h3>
                            <ul className="space-y-3">
                                {links.map((link, index) => (
                                    <li key={index}>
                                        <a
                                            href={link.href}
                                            className="text-gray-400 hover:text-ocean-400 transition-colors duration-200"
                                        >
                                            {link.name}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="bg-gradient-to-r from-ocean-500/10 to-neon-500/10 border border-ocean-500/20 rounded-2xl p-8 mb-12">
                    <div className="flex flex-col lg:flex-row items-center justify-between">
                        <div className="mb-6 lg:mb-0">
                            <h3 className="text-2xl font-bold text-white mb-2">
                                Stay in the Loop
                            </h3>
                            <p className="text-gray-300">
                                Get updates on new chains, features, and
                                exclusive community events.
                            </p>
                        </div>

                        <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto">
                            <input
                                type="email"
                                placeholder="Enter your email"
                                className="px-4 py-3 rounded-lg bg-dark-800/50 border border-ocean-800/30 text-white placeholder-gray-400 focus:border-ocean-500 focus:outline-none w-full sm:w-64"
                            />
                            <button className="bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-ocean-600 hover:to-neon-600 transition-all duration-300 whitespace-nowrap">
                                Subscribe
                            </button>
                        </div>
                    </div>
                </div>

                <div className="border-t border-ocean-800/30 pt-8">
                    <div className="flex flex-col md:flex-row items-center justify-between">
                        <div className="text-gray-400 text-sm mb-4 md:mb-0">
                            © 2025 Mintair. All rights reserved.
                        </div>

                        <div className="text-gray-400 text-sm">
                            All listed company names are trademarks ™ or
                            registered trademarks ® of their respective holders.
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
}
