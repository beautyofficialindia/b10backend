"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useFeatureFlags } from "@/features/platform-settings/providers";

export function AnalyticsNavigation() {
  const pathname = usePathname();
  const { flags } = useFeatureFlags();

  const links = [
    { name: "Overview", href: "/analytics", exact: true },
    { name: "Leads", href: "/analytics/leads", feature: "TRACK_LEADS" },
    { name: "CRM", href: "/analytics/crm", feature: "ENABLE_CRM" },
    { name: "Chat", href: "/analytics/chat", feature: "ENABLE_AI_CHATBOT" },
    { name: "Knowledge", href: "/analytics/knowledge", feature: "ENABLE_KNOWLEDGE_BASE" },
    { name: "Users", href: "/analytics/users" },
  ];

  return (
    <div className="border-b mb-6 px-8">
      <nav className="-mb-px flex space-x-8" aria-label="Tabs">
        {links.map((link) => {
          if (link.feature && flags[link.feature] === false) {
            return null;
          }
          
          const isActive = link.exact 
            ? pathname === link.href 
            : pathname.startsWith(link.href);

          return (
            <Link
              key={link.name}
              href={link.href}
              className={cn(
                isActive
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:border-gray-300 hover:text-gray-700",
                "whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium"
              )}
            >
              {link.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
