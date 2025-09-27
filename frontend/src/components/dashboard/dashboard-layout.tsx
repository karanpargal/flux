"use client";
import React from "react";
import { DashboardLayoutProps } from "../ui/types/page-types";

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
    children,
    className = "",
}) => {
    return (
        
            <div className="max-w-7xl  mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col justify-center min-h-screen">
                <div className="rounded-3xl border-t border-x border-citrus-500/30 glass-effect-transparent">
                <div className="flex flex-col gap-y-4 p-8">
                    <h1 className="text-3xl font-bold text-stone-500">
                        Dashboard
                    </h1>
                    <p className="text-stone-400">
                        Manage your support agents and operations
                    </p>
                </div>
                <div className="glass-effect-citrus rounded-3xl">
                    {children}
                </div>
                </div>
                
            </div>
        
    );
};

export default DashboardLayout;
