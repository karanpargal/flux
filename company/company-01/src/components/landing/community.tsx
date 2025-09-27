"use client";

import { MessageCircle, Twitter, Users, ExternalLink } from "lucide-react";

export default function Community() {
    const socialLinks = [
        {
            icon: MessageCircle,
            name: "Telegram",
            description: "Join our Telegram",
            href: "#",
            color: "from-blue-500 to-blue-600",
            members: "25,000+",
        },
        {
            icon: Twitter,
            name: "Twitter",
            description: "Follow us on X",
            href: "#",
            color: "from-gray-500 to-gray-600",
            members: "50,000+",
        },
        {
            icon: Users,
            name: "Discord",
            description: "Come chat on Discord",
            href: "#",
            color: "from-purple-500 to-purple-600",
            members: "15,000+",
        },
    ];

    const testimonials = [
        {
            name: "Alex Chen",
            role: "Node Operator",
            content:
                "Mintair made it incredibly easy to deploy my first Ethereum node. The process was seamless and the support team was amazing!",
            avatar: "AC",
        },
        {
            name: "Sarah Johnson",
            role: "Blockchain Developer",
            content:
                "I've been using Mintair for multiple chains and the uptime has been exceptional. Highly recommend for anyone serious about running nodes.",
            avatar: "SJ",
        },
        {
            name: "Mike Rodriguez",
            role: "DeFi Enthusiast",
            content:
                "The dashboard is intuitive and the analytics are comprehensive. Mintair has simplified node management for me completely.",
            avatar: "MR",
        },
    ];

    return (
        <section id="community" className="py-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        Social Community
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                        Explore #Mintair community. Join the one-click node
                        operators, no nerds, no complex BS.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                    {socialLinks.map((social, index) => (
                        <a
                            key={index}
                            href={social.href}
                            className="group bg-dark-800/50 backdrop-blur-sm border border-ocean-800/30 rounded-2xl p-8 hover:border-ocean-500/50 transition-all duration-300 hover:scale-105"
                        >
                            <div
                                className={`w-16 h-16 bg-gradient-to-r ${social.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}
                            >
                                <social.icon className="w-8 h-8 text-white" />
                            </div>

                            <h3 className="text-xl font-bold text-white mb-2">
                                {social.name}
                            </h3>
                            <p className="text-gray-300 mb-4">
                                {social.description}
                            </p>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-ocean-400 font-medium">
                                    {social.members} members
                                </span>
                                <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-ocean-400 transition-colors" />
                            </div>
                        </a>
                    ))}
                </div>

                <div className="mb-16">
                    <h3 className="text-3xl font-bold text-white text-center mb-12">
                        What Our Community Says
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {testimonials.map((testimonial, index) => (
                            <div
                                key={index}
                                className="bg-dark-800/50 backdrop-blur-sm border border-ocean-800/30 rounded-2xl p-6"
                            >
                                <div className="flex items-center mb-4">
                                    <div className="w-12 h-12 bg-gradient-to-r from-ocean-500 to-neon-500 rounded-full flex items-center justify-center text-white font-bold mr-4">
                                        {testimonial.avatar}
                                    </div>
                                    <div>
                                        <div className="font-semibold text-white">
                                            {testimonial.name}
                                        </div>
                                        <div className="text-sm text-gray-400">
                                            {testimonial.role}
                                        </div>
                                    </div>
                                </div>
                                <p className="text-gray-300 italic">
                                    &quot;{testimonial.content}&quot;
                                </p>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-gradient-to-r from-ocean-500/10 to-neon-500/10 border border-ocean-500/20 rounded-2xl p-8 text-center">
                    <h3 className="text-2xl font-bold text-white mb-4">
                        Stay Updated
                    </h3>
                    <p className="text-gray-300 mb-6">
                        Get the latest updates on new chains, features, and
                        community events.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                        <input
                            type="email"
                            placeholder="Enter your email"
                            className="flex-1 px-4 py-3 rounded-lg bg-dark-800/50 border border-ocean-800/30 text-white placeholder-gray-400 focus:border-ocean-500 focus:outline-none"
                        />
                        <button className="bg-gradient-to-r from-ocean-500 to-neon-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-ocean-600 hover:to-neon-600 transition-all duration-300">
                            Subscribe
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}
