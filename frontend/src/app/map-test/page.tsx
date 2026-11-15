import {
  UkMap,
} from "@/components/maps/uk-map";


export default function MapTestPage() {
  return (
    <main className="min-h-screen bg-[#f3f3ee] p-12">
      <div className="mx-auto max-w-xl rounded-[28px] bg-[#e8ef7a] p-8">
        <p className="text-xs font-semibold uppercase">
          Your selected area
        </p>

        <h1 className="mt-4 text-6xl tracking-tight">
          Derby
        </h1>

        <p className="mt-2 text-lg">
          East Midlands,
          United Kingdom
        </p>

        <div className="mt-4 h-[420px] text-[#1a1e24]">
          <UkMap
            latitude={52.922}
            longitude={-1.476}
            region="East Midlands"
            locationName="Derby"
            className="h-full w-full"
          />
        </div>
      </div>
    </main>
  );
}
