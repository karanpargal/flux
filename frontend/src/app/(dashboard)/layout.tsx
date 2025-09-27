import Header from "@/components/common/header";
import { ReactNode } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="max-w-7xl mx-auto">
      <Header />
      <div className="py-20">{children}</div>
    </div>
  );
}
