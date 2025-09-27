export default function Chains() {
    return (
        <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-dark-900/50 to-transparent">
            <div className="max-w-7xl mx-auto text-center">
                <h2 className="text-2xl sm:text-3xl font-bold text-white mb-8">
                    <span className="text-gray-300">
                        Everything in one place.
                    </span>
                    <br />
                    <span className="bg-gradient-to-r from-retro-400 to-cyan-400 bg-clip-text text-transparent">
                        Just plug-and-play.
                    </span>
                </h2>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 max-w-4xl mx-auto">
                    {[
                        { name: "Admin Panel", icon: "⚙️" },
                        { name: "CMS", icon: "📝" },
                        { name: "Automation", icon: "🤖" },
                        { name: "Messaging", icon: "💬" },
                        { name: "Analytics", icon: "📊" },
                        { name: "Billing", icon: "💳" },
                    ].map((item, index) => (
                        <div
                            key={item.name}
                            className="retro-card text-center group hover:scale-105 transition-transform duration-300"
                            style={{ animationDelay: `${index * 0.1}s` }}
                        >
                            <div className="text-3xl mb-2 group-hover:animate-bounce">
                                {item.icon}
                            </div>
                            <h3 className="text-sm font-semibold text-retro-300">
                                {item.name}
                            </h3>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
