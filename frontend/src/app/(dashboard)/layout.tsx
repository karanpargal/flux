import Header from "@/components/common/header";
import { ReactNode } from "react";

interface DashboardLayoutProps {
    children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
    return (
        <div
            className="mx-auto font-figtree"
            style={{ fontFamily: '"Figtree", sans-serif' }}
        >
            {/* <Header /> */}
            {children}
        </div>
    );
}
