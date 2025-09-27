import { Suspense } from "react";
import DashboardLayout from "@/components/dashboard/dashboard-layout";
import DashboardPage from "@/components/dashboard/dashboard-page";

export default function Dashboard() {
    return (
        <DashboardLayout>
            <Suspense fallback={<div>Loading...</div>}>
                <DashboardPage />
            </Suspense>
        </DashboardLayout>
    );
}
