import type { Metadata } from "next";
import { Figtree } from "next/font/google";
import "./globals.css";

export const metadata: Metadata = {
    title: "Flux - Streamline Your Support Operations",
    description:
        "Flux helps organizations manage customer support tickets, track issues, and deliver exceptional customer experiences with powerful automation and analytics.",
};

const figtree = Figtree({
    subsets: ["latin"],
});

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body
                className={` w-full min-h-screen antialiased ${figtree.className}`}
            >
                {children}
            </body>
        </html>
    );
}
