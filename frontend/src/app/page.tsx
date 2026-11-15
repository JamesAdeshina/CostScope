import {
  SiteFooter,
} from "@/components/layout/site-footer";

import {
  SiteHeader,
} from "@/components/layout/site-header";

import {
  LocationSearch,
} from "@/components/search/location-search";


export default function Home() {
  return (
    <main className="min-h-screen bg-[#f3f3ee] text-[#1a1e24]">
      <div className="mx-auto max-w-[1536px] px-[18px] min-[1001px]:px-10">
        <SiteHeader active="explore" />
        <LocationSearch />
        <SiteFooter />
      </div>
    </main>
  );
}
