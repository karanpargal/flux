"use client";
import React from "react";
import { DashboardLayoutProps } from "../ui/types/page-types";

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
    children,
    className = "",
}) => {
    return (
        <div className={`min-h-screen bg-cream-50 ${className}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-stone-500 mb-2">
                        Dashboard
                    </h1>
                    <p className="text-stone-400">
                        Manage your support agents and operations
                    </p>
                </div>
                {children}
            </div>
        </div>
    );
};

export default DashboardLayout;
