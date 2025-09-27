import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "@/components/common/header";

const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "RetroFlow - Empower Business Teams Without Breaking the Bank",
    description:
        "Build custom internal tools, centralize operations in a unified dashboard, automate manual workflows, and free up time to focus on what matters.",
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
            </body>
        </html>
    );
}
