"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

export function SettingsSearch() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();
  
  const currentSearch = searchParams.get("search") || "";
  const [value, setValue] = useState(currentSearch);
  const [prevSearch, setPrevSearch] = useState(currentSearch);

  if (currentSearch !== prevSearch) {
    setPrevSearch(currentSearch);
    setValue(currentSearch);
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      if (value === currentSearch) return;

      const params = new URLSearchParams(searchParams);
      if (value) {
        params.set("search", value);
      } else {
        params.delete("search");
      }
      
      // Reset page when searching
      params.delete("page");

      router.push(`${pathname}?${params.toString()}`);
    }, 400); // 400ms debounce as recommended

    return () => clearTimeout(timer);
  }, [value, currentSearch, pathname, router, searchParams]);

  return (
    <div className="relative max-w-sm w-full">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Search settings..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="pl-9 bg-background/50 border-border/50 transition-colors focus:bg-background"
      />
    </div>
  );
}
