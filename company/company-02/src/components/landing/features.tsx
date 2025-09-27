export default function Features() {
    const features = [
        {
            title: "One Integration",
            description:
                "No need to waste time integrating with 10+ tools, and trying to make them play well with each other.",
            icon: "🔗",
            color: "retro",
        },
        {
            title: "Unified Dashboard",
            description:
                "Increase productivity up to 33% by simply having all your work in one place. No switching between multiple apps.",
            icon: "📊",
            color: "cyan",
        },
        {
            title: "Cross-Functional",
            description:
                "Need to send a message to a cohort you just analyzed? Need to A/B test engagement only for users on a free trial? We got you.",
            icon: "🔄",
            color: "pink",
        },
        {
            title: "Customizable",
            description:
                "Extend any objects in the system, bring in your own database, connect external APIs, and build a unified Graph across your workspace.",
            icon: "⚙️",
            color: "retro",
        },
        {
            title: "No-code & Low-code",
            description:
                "Empower non-technical members of your team, while giving your devs the freedom to pick any stack they want.",
            icon: "🛠️",
            color: "cyan",
        },
        {
            title: "AI-powered",
            description:
                "Simply ask AI for the information you need across your product ecosystem. Coming soon.",
            icon: "🤖",
            color: "pink",
        },
    ];

    return (
        <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                {/* Section header */}
                <div className="text-center mb-16">
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6">
                        <span className="text-white">
                            Gain the edge over competitors with our
                        </span>
                        <br />
                        <span className="bg-gradient-to-r from-retro-400 via-cyan-400 to-pink-400 bg-clip-text text-transparent animate-neon-glow">
                            one-of-a-kind platform
                        </span>
                    </h2>
                </div>

                {/* Features grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <div
                            key={feature.title}
                            className="retro-card group hover:scale-105 transition-all duration-300"
                            style={{ animationDelay: `${index * 0.1}s` }}
                        >
                            <div className="flex items-start space-x-4">
                                <div
                                    className={`text-4xl group-hover:animate-bounce ${
                                        feature.color === "retro"
                                            ? "text-retro-400"
                                            : feature.color === "cyan"
                                            ? "text-cyan-400"
                                            : "text-pink-400"
                                    }`}
                                >
                                    {feature.icon}
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-xl font-bold text-white mb-3 group-hover:text-retro-300 transition-colors duration-300">
                                        {feature.title}
                                    </h3>
                                    <p className="text-gray-300 leading-relaxed">
                                        {feature.description}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Build out section */}
                <div className="mt-20 text-center">
                    <div className="retro-card max-w-4xl mx-auto">
                        <h3 className="text-2xl sm:text-3xl font-bold text-white mb-4">
                            Build out 360° views and internal tooling
                        </h3>
                        <p className="text-gray-300 text-lg mb-6">
                            CRUD / Customizable UI / Forms / Wizards
                        </p>
                        <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-400">
                            <span className="px-3 py-1 bg-retro-500/20 rounded-full border border-retro-500/30">
                                Replace these SaaS tools
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
