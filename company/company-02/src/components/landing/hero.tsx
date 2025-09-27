export default function Hero() {
    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
            {/* Animated background elements */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-retro-500/10 rounded-full blur-3xl animate-float-retro"></div>
                <div
                    className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-float-retro"
                    style={{ animationDelay: "1s" }}
                ></div>
                <div
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-pink-500/10 rounded-full blur-2xl animate-float-retro"
                    style={{ animationDelay: "2s" }}
                ></div>
            </div>

            {/* Scan line effect */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="w-full h-1 bg-gradient-to-r from-transparent via-retro-500 to-transparent animate-scan-line"></div>
            </div>

            <div className="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto">
                {/* Main heading */}
                <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold mb-6 leading-tight">
                    <span className="block text-white mb-2">
                        Empower business teams
                    </span>
                    <span className="block bg-gradient-to-r from-retro-400 via-cyan-400 to-pink-400 bg-clip-text text-transparent animate-neon-glow">
                        without breaking the bank
                    </span>
                </h1>

                {/* Subheading */}
                <p className="text-lg sm:text-xl lg:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed">
                    DashX helps you build{" "}
                    <span className="text-retro-400 font-semibold">
                        custom internal tools
                    </span>
                    , centralize operations in a unified dashboard, automate
                    manual workflows, and frees up time to{" "}
                    <span className="text-cyan-400 font-semibold">
                        focus on what matters
                    </span>
                    .
                </p>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
                    <button className="retro-button text-lg px-8 py-4 animate-retro-pulse">
                        Start Free Trial
                    </button>
                    <button className="text-white border-2 border-retro-500 hover:bg-retro-500/20 transition-all duration-300 px-8 py-4 rounded-lg font-semibold text-lg">
                        Schedule a Demo
                    </button>
                </div>

                {/* Trusted by section */}
                <div className="mb-16">
                    <p className="text-gray-400 text-sm uppercase tracking-wider mb-8">
                        Trusted by the next generation of companies
                    </p>
                    <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
                        {/* Placeholder logos - you can replace with actual company logos */}
                        <div className="h-8 w-24 bg-gray-600 rounded animate-pulse"></div>
                        <div className="h-8 w-24 bg-gray-600 rounded animate-pulse"></div>
                        <div className="h-8 w-24 bg-gray-600 rounded animate-pulse"></div>
                        <div className="h-8 w-24 bg-gray-600 rounded animate-pulse"></div>
                        <div className="h-8 w-24 bg-gray-600 rounded animate-pulse"></div>
                    </div>
                </div>

                {/* Feature grid preview */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 max-w-4xl mx-auto">
                    {[
                        { name: "Admin Panel", icon: "⚙️" },
                        { name: "CMS", icon: "📝" },
                        { name: "Automation", icon: "🤖" },
                        { name: "Messaging", icon: "💬" },
                        { name: "Analytics", icon: "📊" },
                        { name: "Billing", icon: "💳" },
                    ].map((feature, index) => (
                        <div
                            key={feature.name}
                            className="retro-card text-center group hover:scale-105 transition-transform duration-300"
                            style={{ animationDelay: `${index * 0.1}s` }}
                        >
                            <div className="text-3xl mb-2 group-hover:animate-bounce">
                                {feature.icon}
                            </div>
                            <h3 className="text-sm font-semibold text-retro-300">
                                {feature.name}
                            </h3>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
