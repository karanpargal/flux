"use client";
import Header from "@/components/common/header";
import { ReactNode } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { useOrganization } from "@/lib/hooks";

interface DashboardLayoutProps {
    children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
    const pathname = usePathname();
    const searchParams = useSearchParams();

    // Get orgId from URL params
    const urlOrgId = searchParams.get("orgId");

    // Check if organization data exists (user is authenticated)
    const { data: organization, loading: orgLoading } =
        useOrganization(urlOrgId);

    // Determine if user is authenticated
    const isAuthenticated = !!(urlOrgId && organization && !orgLoading);

    // Show header only for authenticated users on dashboard routes (not login/signup)
    const shouldShowHeader =
        isAuthenticated &&
        (pathname === "/dashboard" ||
            pathname.startsWith("/new-agent") ||
            pathname.startsWith("/agent"));

    return (
        <div
            className="mx-auto font-figtree"
            style={{ fontFamily: '"Figtree", sans-serif' }}
        >
            {shouldShowHeader && <Header />}
            {children}
        </div>
    );
}
