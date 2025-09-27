import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "@/components/common/header";
import FloatingChatWidget from "@/components/floating-chat-widget";

const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "NodeFlow - One Click Blockchain Infrastructure",
    description:
        "Deploy blockchain nodes effortlessly with NodeFlow's one-click solution. Making decentralized infrastructure accessible to everyone.",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body
                className={`${geistSans.variable} ${geistMono.variable} min-h-screen antialiased`}
            >
                <div className="max-w-7xl mx-auto">
                    <Header />
                    <main>{children}</main>
                </div>
                <FloatingChatWidget
                    title="NodeFlow Assistant"
                    agentId="nodeflow-agent"
                    organizationId="nodeflow-org"
                />
            </body>
        </html>
    );
}
