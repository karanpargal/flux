export default function HowItWorks() {
    const steps = [
        {
            step: "01",
            title: "Everything in one place",
            subtitle: "Just plug-and-play",
            description:
                "Connect all your tools and data sources in one unified platform. No more switching between multiple apps or dealing with integration headaches.",
            icon: "🔌",
        },
        {
            step: "02",
            title: "Customize & Automate",
            subtitle: "Build what you need",
            description:
                "Create custom workflows, automate repetitive tasks, and build internal tools that perfectly fit your team's needs.",
            icon: "⚡",
        },
        {
            step: "03",
            title: "Scale & Optimize",
            subtitle: "Focus on what matters",
            description:
                "With everything centralized and automated, your team can focus on high-impact work instead of managing tools and processes.",
            icon: "🚀",
        },
    ];

    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-transparent to-dark-900/50">
            <div className="max-w-7xl mx-auto">
                {/* Section header */}
                <div className="text-center mb-16">
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6">
                        <span className="text-white">How it works</span>
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                        Three simple steps to transform your business operations
                    </p>
                </div>

                {/* Steps */}
                <div className="space-y-16">
                    {steps.map((step, index) => (
                        <div
                            key={step.step}
                            className={`flex flex-col lg:flex-row items-center gap-12 ${
                                index % 2 === 1 ? "lg:flex-row-reverse" : ""
                            }`}
                        >
                            {/* Content */}
                            <div className="flex-1 text-center lg:text-left">
                                <div className="retro-card max-w-lg mx-auto lg:mx-0">
                                    <div className="flex items-center justify-center lg:justify-start mb-4">
                                        <span className="text-6xl mr-4">
                                            {step.icon}
                                        </span>
                                        <div>
                                            <div className="text-retro-400 font-bold text-sm tracking-wider">
                                                STEP {step.step}
                                            </div>
                                            <h3 className="text-2xl font-bold text-white">
                                                {step.title}
                                            </h3>
                                        </div>
                                    </div>
                                    <p className="text-retro-300 font-semibold text-lg mb-4">
                                        {step.subtitle}
                                    </p>
                                    <p className="text-gray-300 leading-relaxed">
                                        {step.description}
                                    </p>
                                </div>
                            </div>

                            {/* Visual placeholder */}
                            <div className="flex-1 flex justify-center">
                                <div className="w-full max-w-md h-64 retro-card flex items-center justify-center">
                                    <div className="text-center">
                                        <div className="text-6xl mb-4 animate-float-retro">
                                            {step.icon}
                                        </div>
                                        <div className="text-gray-400 text-sm">
                                            Interactive Demo Coming Soon
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* CTA */}
                <div className="text-center mt-16">
                    <div className="retro-card max-w-2xl mx-auto">
                        <h3 className="text-2xl font-bold text-white mb-4">
                            Ready to get started?
                        </h3>
                        <p className="text-gray-300 mb-6">
                            Join thousands of teams already using DashX to
                            streamline their operations
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button className="retro-button">
                                Start Free Trial
                            </button>
                            <button className="text-white border-2 border-retro-500 hover:bg-retro-500/20 transition-all duration-300 px-6 py-3 rounded-lg font-semibold">
                                Schedule Demo
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
