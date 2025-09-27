import { ReactNode } from "react";
import "./embed.css";

interface EmbedLayoutProps {
    children: ReactNode;
}

export default function EmbedLayout({ children }: EmbedLayoutProps) {
    return (
        <html lang="en">
            <body className="embed-body">
                <div className="embed-standalone-container">{children}</div>
            </body>
        </html>
    );
}
