import Hero from "@/components/landing/hero";
import HowItWorks from "@/components/landing/how-it-works";
import Features from "@/components/landing/features";
import Chains from "@/components/landing/chains";
import Community from "@/components/landing/community";
import Footer from "@/components/common/footer";

export default function Home() {
    return (
        <>
            <Hero />
            <HowItWorks />
            <Features />
            <Chains />
            <Community />
            <Footer />
        </>
    );
}
