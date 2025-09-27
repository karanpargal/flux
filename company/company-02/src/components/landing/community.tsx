export default function Community() {
    const testimonials = [
        {
            quote: "DashX made it extremely easy for our entire team to manage everything in one place - from content management to sales & marketing!",
            author: "Narayan Gopalan",
            role: "Founder, IxDEAS",
            avatar: "👨‍💼",
        },
    ];

    const companies = [
        { name: "TechCorp", logo: "🏢" },
        { name: "StartupXYZ", logo: "🚀" },
        { name: "InnovateLab", logo: "🔬" },
        { name: "DataFlow", logo: "📊" },
        { name: "CloudSync", logo: "☁️" },
        { name: "NextGen", logo: "⚡" },
    ];

    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                {/* Testimonials */}
                <div className="text-center mb-16">
                    <h2 className="text-3xl sm:text-4xl font-bold mb-12">
                        <span className="text-white">
                            What our customers have to say
                        </span>
                    </h2>

                    <div className="max-w-4xl mx-auto">
                        {testimonials.map((testimonial, index) => (
                            <div
                                key={index}
                                className="retro-card text-center animate-retro-pulse"
                            >
                                <div className="text-6xl mb-6">
                                    {testimonial.avatar}
                                </div>
                                <blockquote className="text-xl lg:text-2xl text-gray-300 italic mb-6 leading-relaxed">
                                    "{testimonial.quote}"
                                </blockquote>
                                <div className="text-center">
                                    <div className="font-bold text-white text-lg">
                                        {testimonial.author}
                                    </div>
                                    <div className="text-retro-400">
                                        {testimonial.role}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Partner section */}
                <div className="text-center mb-16">
                    <h3 className="text-2xl font-bold text-white mb-8">
                        Trusted by innovative companies
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
                        {companies.map((company, index) => (
                            <div
                                key={company.name}
                                className="retro-card text-center group hover:scale-105 transition-transform duration-300"
                                style={{ animationDelay: `${index * 0.1}s` }}
                            >
                                <div className="text-3xl mb-2 group-hover:animate-bounce">
                                    {company.logo}
                                </div>
                                <div className="text-sm font-semibold text-retro-300">
                                    {company.name}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* CTA Section */}
                <div className="text-center">
                    <div className="retro-card max-w-4xl mx-auto">
                        <h3 className="text-3xl sm:text-4xl font-bold text-white mb-6">
                            Your long-term technology partner
                        </h3>
                        <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
                            We work closely with the best teams to deliver
                            tailor-made portals that increase operational
                            leverage and improve business efficiency.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button className="retro-button text-lg px-8 py-4">
                                Schedule a Demo
                            </button>
                            <button className="text-white border-2 border-retro-500 hover:bg-retro-500/20 transition-all duration-300 px-8 py-4 rounded-lg font-semibold text-lg">
                                Contact Us
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
