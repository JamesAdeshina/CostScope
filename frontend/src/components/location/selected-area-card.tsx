"use client";

import {
  useEffect,
  useRef,
} from "react";

import { UkMap } from "@/components/maps/uk-map";


interface SelectedAreaCardProps {
  name: string;
  region?: string | null;
  postcode?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}


export function SelectedAreaCard({
  name,
  region,
  postcode,
  latitude,
  longitude,
}: SelectedAreaCardProps) {
  const cardRef =
    useRef<HTMLElement>(null);

  const mounted =
    useRef(false);

  /* Small "settle" pop when a new area is chosen (not on first load). */
  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;

      return;
    }

    if (
      window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches
    ) {
      return;
    }

    cardRef.current?.animate(
      [
        { transform: "scale(.98)" },
        { transform: "none" },
      ],
      {
        duration: 350,
        easing: "ease-out",
      },
    );
  }, [name, postcode]);

  return (
    <section
      ref={cardRef}
      className="relative min-h-[260px] overflow-hidden rounded-[28px] bg-[#e8ef7a] px-7 py-[26px]"
    >
      <div className="relative z-10">
        <p className="text-xs uppercase tracking-[0.02em]">
          Your selected area
        </p>

        <h2 className="mb-1 mt-[22px] text-[clamp(44px,5vw,64px)] font-normal leading-[1.1]">
          {name}
        </h2>

        <p className="text-[15px]">
          {region
            ? `${region}, United Kingdom`
            : "United Kingdom"}
        </p>

        <div className="mt-[38px] flex flex-wrap items-center gap-[18px]">
          {postcode && (
            <span className="rounded-full bg-[#1a1e24] px-5 py-[11px] text-sm font-medium text-white">
              {postcode}
            </span>
          )}

          <span className="text-[13px]">
            Local insights. National context.
          </span>
        </div>
      </div>

      <div className="absolute bottom-[18px] right-[34px] top-[18px] w-[43%] text-[#1a1e24]">
        <UkMap
          latitude={latitude}
          longitude={longitude}
          region={region}
          locationName={name}
          className="h-full w-full"
        />
      </div>
    </section>
  );
}
