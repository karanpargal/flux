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
                <iframe
                    src={process.env.NEXT_PUBLIC_SUPPORTIFY_EMBED_URL}
                    width="350"
                    height="500"
                    style={{
                        position: "fixed",
                        bottom: "20px",
                        right: "20px",
                        borderRadius: "16px",
                        boxShadow: "0 10px 40px rgba(0,0,0,0.15)",
                        zIndex: "9999",
                    }}
                    title="Support Chat"
                />
                <div className="max-w-7xl mx-auto">
                    <Header />
                    <main>{children}</main>
                </div>
            </body>
        </html>
    );
}
