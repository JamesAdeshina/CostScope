"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import type {
  LocationOverviewResponse,
  MetricHistoryResponse,
} from "@/types/api";

import {
  CostOfLivingIndex,
} from "@/components/explore/cost-of-living-index";

import {
  LocationCompare,
} from "@/components/explore/location-compare";

import {
  RentHistoryChart,
} from "@/components/charts/rent-history-chart";

import {
  UkMap,
} from "@/components/maps/uk-map";

import {
  OfficialSources,
} from "@/components/sources/official-sources";


interface ExploreLowerSectionProps {
  rentHistory:
    | MetricHistoryResponse
    | null;

  locationName: string;

  overview:
    LocationOverviewResponse;

  region?:
    | string
    | null;

  latitude?:
    | number
    | null;

  longitude?:
    | number
    | null;
}


function formatMonthYear(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    "en-GB",
    {
      month: "short",
      year: "numeric",
    },
  ).format(
    new Date(
      `${value}T00:00:00`,
    ),
  );
}


export function ExploreLowerSection({
  rentHistory,
  locationName,
  overview,
  region,
  latitude,
  longitude,
}: ExploreLowerSectionProps) {
  const [
    compareOpen,
    setCompareOpen,
  ] = useState(false);

  const [
    leaving,
    setLeaving,
  ] = useState(false);

  const gridRef =
    useRef<HTMLElement>(
      null,
    );

  const compareRef =
    useRef<HTMLDivElement>(
      null,
    );

  const toggled =
    useRef(false);

  const timer =
    useRef<
      number | null
    >(null);


  /*
   * Clear delayed compare transition
   * if the component unmounts.
   */
  useEffect(() => {
    return () => {
      if (
        timer.current !==
        null
      ) {
        window.clearTimeout(
          timer.current,
        );
      }
    };
  }, []);


  /*
   * Smoothly move the viewport between
   * the compact comparison card and
   * the expanded comparison panel.
   */
  useEffect(() => {
    if (
      !toggled.current
    ) {
      return;
    }

    const target =
      compareOpen
        ? compareRef.current
        : gridRef.current;

    const frame =
      requestAnimationFrame(
        () => {
          target?.scrollIntoView(
            {
              behavior:
                "smooth",
              block:
                "center",
            },
          );
        },
      );

    return () => {
      cancelAnimationFrame(
        frame,
      );
    };
  }, [
    compareOpen,
  ]);


  /*
   * Fade/shrink the mini comparison
   * card before opening the full
   * comparison panel.
   */
  function openCompare() {
    toggled.current =
      true;

    setLeaving(
      true,
    );

    timer.current =
      window.setTimeout(
        () => {
          setCompareOpen(
            true,
          );

          setLeaving(
            false,
          );
        },
        250,
      );
  }


  function closeCompare() {
    toggled.current =
      true;

    setCompareOpen(
      false,
    );
  }


  /*
   * Build the display range for the
   * rent history card.
   */
  const observations =
    rentHistory?.observations ??
    [];

  const range =
    observations.length >
    0
      ? `${formatMonthYear(
          observations[0]
            .reference_period,
        )} → ${formatMonthYear(
          observations[
            observations.length -
              1
          ].reference_period,
        )}`
      : locationName;


  return (
    <>
      {/* =====================================================
          LOWER EXPLORE GRID
          ===================================================== */}

      <section
        ref={gridRef}
        className={`mt-[18px] grid items-start gap-[18px] ${
          compareOpen
            ? "min-[1001px]:grid-cols-[1fr_1.5fr]"
            : "min-[1001px]:grid-cols-[0.9fr_1.5fr_1fr]"
        }`}
      >
        {/* ===================================================
            COST OF LIVING INDEX
            =================================================== */}

        <CostOfLivingIndex />


        {/* ===================================================
            RENT HISTORY
            =================================================== */}

        <article className="min-w-0 overflow-hidden rounded-[28px] bg-white p-[22px] text-[#1a1e24]">
          <div className="float-right flex gap-3.5 text-[11px] text-[#0a84ff]">
            <span>
              ━{" "}
              {
                locationName
              }
            </span>
          </div>

          <h2 className="text-[24px] font-medium tracking-[-0.01em] text-[#1a1e24]">
            Average monthly private rent
          </h2>

          <p className="mb-2 mt-1 text-sm text-[#6b6f72]">
            {range}
          </p>

          {rentHistory ? (
            <RentHistoryChart
              history={
                rentHistory
              }
            />
          ) : (
            <div className="grid min-h-[230px] place-items-center rounded-[20px] bg-[#f3f3ee]">
              <p className="px-6 text-center text-sm text-[#6b6f72]">
                Rent history will appear here when an area is selected.
              </p>
            </div>
          )}
        </article>


        {/* ===================================================
            MINI COMPARE CARD
            =================================================== */}

        {!compareOpen && (
          <article
            className={`cs-rise relative flex min-h-[310px] flex-col overflow-hidden rounded-[28px] bg-white p-[22px] text-[#1a1e24] transition-[opacity,transform] duration-[250ms] ${
              leaving
                ? "scale-[.96] opacity-0"
                : ""
            }`}
          >
            {/* ===============================================
                MAP BACKGROUND
                ================================================= */}

            <div
              className="
                absolute bottom-3 right-3 top-3 z-0 w-[52%]
                [&_svg]:h-full
                [&_svg]:w-full
                [&_path]:cursor-pointer
                [&_path]:transition-colors
                [&_path]:duration-200
                [&_path:hover]:fill-[#9a9a96]
              "
            >
              <UkMap
                latitude={
                  latitude
                }
                longitude={
                  longitude
                }
                region={
                  region
                }
                locationName={
                  locationName
                }
                outlineColor="#ffffff"
                className="h-full w-full"
              />
            </div>


            {/* ===============================================
                CONTENT
                pointer-events-none keeps map hoverable.
                The CTA re-enables pointer interaction.
                ================================================= */}

            <div className="pointer-events-none relative z-10 flex flex-1 flex-col">
              <div className="flex items-center gap-3">
                <span className="grid h-12 w-12 shrink-0 place-items-center rounded-[16px] bg-[#ebebe5] text-[#1a1e24]">
                  <svg
                    width="22"
                    height="22"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M12 21s-7-6.2-7-11a7 7 0 1 1 14 0c0 4.8-7 11-7 11Z" />

                    <circle
                      cx="12"
                      cy="10"
                      r="2.5"
                    />
                  </svg>
                </span>

                <span className="text-xs font-medium uppercase tracking-[0.01em] text-[#6b6f72]">
                  Compare locations
                </span>
              </div>


              <h2 className="mb-[14px] mt-[22px] max-w-[62%] text-[32px] font-medium leading-[1.1] tracking-[-0.01em] text-[#1a1e24]">
                How does your area
                <br />
                compare?
              </h2>

              <p className="max-w-[62%] text-sm leading-[1.45] text-[#6b6f72]">
                Compare rent, earnings, energy costs and unemployment across UK locations.
              </p>


              <button
                type="button"
                onClick={
                  openCompare
                }
                className="pointer-events-auto mt-auto inline-flex w-[62%] min-w-[200px] items-center justify-center gap-3 self-start rounded-full bg-[#1a1e24] px-7 py-[14px] text-sm font-medium text-white transition hover:-translate-y-px hover:bg-[#2b3139] active:scale-[0.97]"
              >
                <span className="whitespace-nowrap">
                  Compare locations
                </span>

                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                  className="shrink-0"
                >
                  <path d="M2 8h12M9 3l5 5-5 5" />
                </svg>
              </button>
            </div>


            <small className="pointer-events-none absolute bottom-4 right-[22px] z-10 text-xs text-[#6b6f72]">
              UK locations
            </small>
          </article>
        )}
      </section>


      {/* =====================================================
          EXPANDED LOCATION COMPARISON
          ===================================================== */}

      {compareOpen && (
        <div
          ref={
            compareRef
          }
        >
          <LocationCompare
            primary={
              overview
            }
            onClose={
              closeCompare
            }
          />
        </div>
      )}


      {/* =====================================================
          OFFICIAL DATA STRIP
          This stays LAST.
          ===================================================== */}

      <OfficialSources />
    </>
  );
}