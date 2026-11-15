"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  getLocationOverview,
  getPostcodeOverview,
  getRentHistory,
  searchLocations,
} from "@/lib/api/client";

import {
  formatCurrency,
  formatDate,
  formatPercent,
} from "@/lib/formatters";

import type {
  LocationOverviewResponse,
  LocationSearchResult,
  MetricHistoryResponse,
} from "@/types/api";

import {
  ExploreLowerSection,
} from "@/components/explore/explore-lower-section";

import {
  SelectedAreaCard,
} from "@/components/location/selected-area-card";

import {
  CountUp,
} from "@/components/ui/count-up";


const DEFAULT_POSTCODE = "DE1 1AA";


function looksLikePostcode(
  value: string,
): boolean {
  return /^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$/i.test(
    value.trim(),
  );
}


export function LocationSearch() {
  const [query, setQuery] =
    useState(DEFAULT_POSTCODE);

  const [suggestions, setSuggestions] =
    useState<LocationSearchResult[]>([]);

  const [selectedLocation, setSelectedLocation] =
    useState<LocationSearchResult | null>(null);

  const [overview, setOverview] =
    useState<LocationOverviewResponse | null>(null);

  const [rentHistory, setRentHistory] =
    useState<MetricHistoryResponse | null>(null);

  const [postcodeLabel, setPostcodeLabel] =
    useState<string | null>(DEFAULT_POSTCODE);

  const [coordinates, setCoordinates] =
    useState<{
      latitude: number;
      longitude: number;
    } | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [searching, setSearching] =
    useState(false);


  useEffect(() => {
    let active = true;

    async function loadInitialArea() {
      setLoading(true);
      setError(null);

      try {
        const response =
          await getPostcodeOverview(
            DEFAULT_POSTCODE,
          );

        const history =
          await getRentHistory(
            response.overview.location
              .location_code,
          );

        if (!active) {
          return;
        }

        setOverview(response.overview);
        setRentHistory(history);
        setPostcodeLabel(
          response.postcode.postcode,
        );
        setCoordinates({
          latitude:
            response.postcode.latitude,
          longitude:
            response.postcode.longitude,
        });
        setQuery(
          response.postcode.postcode,
        );
      } catch (requestError) {
        if (!active) {
          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load CostScope data.",
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadInitialArea();

    return () => {
      active = false;
    };
  }, []);


  useEffect(() => {
    const value = query.trim();

    if (
      value.length < 2 ||
      looksLikePostcode(value) ||
      selectedLocation
    ) {
      setSuggestions([]);
      return;
    }

    const timeout = window.setTimeout(
      async () => {
        setSearching(true);

        try {
          const results =
            await searchLocations(value);

          setSuggestions(
            results.slice(0, 8),
          );
        } catch {
          setSuggestions([]);
        } finally {
          setSearching(false);
        }
      },
      250,
    );

    return () => {
      window.clearTimeout(timeout);
    };
  }, [query, selectedLocation]);


  async function loadLocation(
    locationCode: string,
  ) {
    setLoading(true);
    setError(null);
    setSuggestions([]);
    setCoordinates(null);
    setPostcodeLabel(null);

    try {
      const [
        overviewResponse,
        historyResponse,
      ] = await Promise.all([
        getLocationOverview(
          locationCode,
        ),
        getRentHistory(
          locationCode,
        ),
      ]);

      setOverview(overviewResponse);
      setRentHistory(historyResponse);
    } catch (requestError) {
      setOverview(null);
      setRentHistory(null);
      setCoordinates(null);

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load CostScope data.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function loadPostcode(
    postcode: string,
  ) {
    setLoading(true);
    setError(null);
    setSuggestions([]);

    try {
      const response =
        await getPostcodeOverview(
          postcode,
        );

      const history =
        await getRentHistory(
          response.overview.location
            .location_code,
        );

      setOverview(response.overview);
      setRentHistory(history);
      setPostcodeLabel(
        response.postcode.postcode,
      );
      setCoordinates({
        latitude:
          response.postcode.latitude,
        longitude:
          response.postcode.longitude,
      });
      setQuery(
        response.postcode.postcode,
      );
      setSelectedLocation(null);
    } catch (requestError) {
      setOverview(null);
      setRentHistory(null);
      setCoordinates(null);

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load CostScope data.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const value = query.trim();

    if (!value) {
      return;
    }

    if (looksLikePostcode(value)) {
      await loadPostcode(value);
      return;
    }

    if (selectedLocation) {
      await loadLocation(
        selectedLocation.location_code,
      );
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const results =
        await searchLocations(value);

      if (!results.length) {
        throw new Error(
          "No matching location found.",
        );
      }

      const location = results[0];

      setSelectedLocation(location);
      setQuery(location.name);

      await loadLocation(
        location.location_code,
      );
    } catch (requestError) {
      setOverview(null);
      setRentHistory(null);
      setCoordinates(null);

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load CostScope data.",
      );
    } finally {
      setLoading(false);
    }
  }


  function handleQueryChange(
    value: string,
  ) {
    setQuery(value);
    setSelectedLocation(null);
  }


  function chooseLocation(
    location: LocationSearchResult,
  ) {
    setSelectedLocation(location);
    setQuery(location.name);
    setSuggestions([]);

    void loadLocation(
      location.location_code,
    );
  }


  const locationName =
    overview?.location.name ??
    "Derby";

  const locationRegion =
    overview?.location
      .region_or_country ??
    "East Midlands";


  return (
    <>
      <section className="grid items-start gap-10 min-[1001px]:grid-cols-[1.25fr_1fr]">
        <div>
          <p className="text-xs uppercase tracking-[0.02em] text-[#6b6f72]">
            The local cost of living, explained
          </p>

          <h1 className="mb-[22px] mt-[14px] text-[clamp(44px,6vw,72px)] font-normal leading-[1.05] tracking-[-0.02em] text-[#1a1e24]">
            Your area.
            <br />
            A clearer picture.
          </h1>

          <p className="mb-[22px] max-w-[760px] text-[17px] leading-[1.45] text-[#6b6f72]">
            Explore rent, earnings and the wider economy with official UK data.
          </p>

          <form
            onSubmit={handleSubmit}
            className="relative flex max-w-[680px] flex-wrap items-center gap-[14px] rounded-[24px] border border-[#e4e4dd] bg-white py-1.5 pl-[18px] pr-1.5 min-[561px]:flex-nowrap min-[561px]:rounded-full"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              stroke="#1a1e24"
              strokeWidth="1.6"
              className="shrink-0"
              aria-hidden="true"
            >
              <circle cx="9" cy="9" r="6.5" />
              <path d="m14 14 4 4" />
            </svg>

            <div className="relative min-w-[110px] flex-1 min-[561px]:max-w-[180px]">
              <input
                type="text"
                value={query}
                onChange={(event) =>
                  handleQueryChange(
                    event.target.value,
                  )
                }
                aria-label="Postcode or location"
                autoComplete="off"
                placeholder="Postcode or city"
                className="w-full border-0 bg-transparent py-2 text-[15px] text-[#1a1e24] outline-none placeholder:text-[#9a9d9e]"
              />

              {suggestions.length > 0 && (
                <div className="absolute left-[-52px] top-[50px] z-50 w-[min(520px,calc(100vw-36px))] overflow-hidden rounded-2xl border border-[#e4e4dd] bg-white shadow-[0_18px_50px_rgba(26,30,36,.12)]">
                  {suggestions.map(
                    (location) => (
                      <button
                        key={
                          location.location_code
                        }
                        type="button"
                        onClick={() =>
                          chooseLocation(
                            location,
                          )
                        }
                        className="flex w-full items-center justify-between gap-4 border-b border-[#eeeeea] bg-white px-5 py-3.5 text-left transition last:border-0 hover:bg-[#f6f6f2]"
                      >
                        <span>
                          <span className="block text-sm font-medium text-[#1a1e24]">
                            {location.name}
                          </span>

                          {location.region_or_country && (
                            <span className="mt-0.5 block text-xs text-[#6b6f72]">
                              {
                                location.region_or_country
                              }
                            </span>
                          )}
                        </span>

                        <svg
                          width="12"
                          height="12"
                          viewBox="0 0 14 14"
                          fill="none"
                          stroke="#6b6f72"
                          strokeWidth="1.6"
                          aria-hidden="true"
                        >
                          <path d="m5 2 5 5-5 5" />
                        </svg>
                      </button>
                    ),
                  )}
                </div>
              )}
            </div>

            <span className="hidden min-w-0 flex-1 border-l border-[#e4e4dd] pl-4 text-[15px] text-[#6b6f72] min-[561px]:block">
              {locationName}, {locationRegion}
            </span>

            <button
              type="submit"
              disabled={loading}
              className="ml-auto inline-flex shrink-0 items-center gap-2.5 rounded-full bg-[#1a1e24] px-[22px] py-[13px] text-sm font-medium text-white transition hover:-translate-y-px hover:bg-[#2b3139] active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Loading..."
                : "Explore area"}

              {!loading && (
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 14 14"
                  fill="none"
                  stroke="white"
                  strokeWidth="1.8"
                  aria-hidden="true"
                >
                  <path d="m5 2 5 5-5 5" />
                </svg>
              )}
            </button>
          </form>

          {searching && (
            <p className="mt-2 text-xs text-[#6b6f72]">
              Searching…
            </p>
          )}

          {error && (
            <p
              role="alert"
              className="mt-3 max-w-[680px] text-sm text-red-800"
            >
              {error}
            </p>
          )}
        </div>

        <SelectedAreaCard
          name={locationName}
          region={locationRegion}
          postcode={postcodeLabel}
          latitude={
            coordinates?.latitude
          }
          longitude={
            coordinates?.longitude
          }
        />
      </section>

      {overview && (
        <>
          <div className="mb-[14px] mt-[34px] flex flex-col gap-1 text-sm text-[#6b6f72] min-[561px]:flex-row min-[561px]:items-baseline min-[561px]:justify-between">
            <h2 className="text-[25px] font-normal tracking-[-0.01em] text-[#1a1e24]">
              The numbers that matter
            </h2>

            <span>
              Local figures, with UK inflation for context
            </span>
          </div>

          <section className="grid gap-[18px] min-[561px]:grid-cols-2 min-[1001px]:grid-cols-4">
            {overview.rent && (
              <article className="flex min-h-[196px] flex-col rounded-[28px] bg-[#1a1e24] p-[22px] text-white">
                <p className="mb-3 flex items-center gap-2.5 text-[15px] text-white">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="#e8ef7a"
                    strokeWidth="1.5"
                    aria-hidden="true"
                  >
                    <path d="M3 9l7-6 7 6v8H3z" />
                  </svg>
                  Average private rent
                </p>

                <p className="text-[46px] font-medium leading-none tracking-[-0.02em] text-white">
                  <CountUp
                    value={
                      overview.rent.monthly_rent
                    }
                    format={(value) =>
                      formatCurrency(
                        Math.round(value),
                      )
                    }
                  />
                </p>

                <p className="mt-1 text-[13px] text-[#b9bdc1]">
                  per month
                </p>

                <p className="mt-2 text-[13px] text-[#e8ef7a]">
                  ↑ {formatPercent(
                    overview.rent
                      .monthly_change_percent,
                    2,
                  )} monthly · ↑ {formatPercent(
                    overview.rent
                      .annual_change_percent,
                    2,
                  )} annually
                </p>

                <p className="mt-auto border-t border-[#3a4048] pt-[9px] text-[11px] text-[#b9bdc1]">
                  Reference period: {formatDate(
                    overview.rent
                      .reference_period,
                  )}
                </p>
              </article>
            )}

            {overview.earnings && (
              <article className="flex min-h-[196px] flex-col rounded-[28px] bg-white p-[22px] text-[#1a1e24]">
                <p className="mb-3 flex items-center gap-2.5 text-[15px]">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="#1a1e24"
                    strokeWidth="1.5"
                    aria-hidden="true"
                  >
                    <rect
                      x="2"
                      y="6"
                      width="16"
                      height="11"
                      rx="2"
                    />
                    <path d="M7 6V4h6v2" />
                  </svg>
                  Median annual earnings
                </p>

                <p className="text-[46px] font-medium leading-none tracking-[-0.02em]">
                  <CountUp
                    value={
                      overview.earnings
                        .median_annual_pay
                    }
                    format={(value) =>
                      formatCurrency(
                        Math.round(value),
                      )
                    }
                  />
                </p>

                <p className="mt-1 text-[13px] text-[#6b6f72]">
                  per year
                </p>

                <p className="mt-2 text-[13px] text-[#1a8f5c]">
                  ↑ {formatPercent(
                    overview.earnings
                      .annual_change_percent,
                  )} annual change
                </p>

                <p className="mt-auto border-t border-[#e8e8e2] pt-[9px] text-[11px] text-[#6b6f72]">
                  Reference period: {formatDate(
                    overview.earnings
                      .reference_period,
                  )}
                </p>
              </article>
            )}

            {overview.inflation && (
              <article className="flex min-h-[196px] flex-col rounded-[28px] bg-white p-[22px] text-[#1a1e24]">
                <p className="mb-3 flex items-center gap-2.5 text-[15px]">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="#1a1e24"
                    strokeWidth="1.5"
                    aria-hidden="true"
                  >
                    <path d="M3 4h3l2 9h8l1-6H7" />
                    <circle cx="9" cy="16" r="1" />
                    <circle cx="15" cy="16" r="1" />
                  </svg>
                  UK inflation
                </p>

                <p className="text-[46px] font-medium leading-none tracking-[-0.02em]">
                  <CountUp
                    value={
                      overview.inflation
                        .annual_rate_percent
                    }
                    format={(value) =>
                      formatPercent(value)
                    }
                  />
                </p>

                <p className="mt-1 text-[13px] text-[#6b6f72]">
                  annual rate
                </p>

                <p className="mt-2 text-[13px] text-[#6b6f72]">
                  {formatPercent(
                    overview.inflation
                      .monthly_rate_percent,
                  )} monthly rate
                </p>

                <p className="mt-auto border-t border-[#e8e8e2] pt-[9px] text-[11px] text-[#6b6f72]">
                  Reference period: {formatDate(
                    overview.inflation
                      .reference_period,
                  )}
                </p>
              </article>
            )}

            {overview.unemployment && (
              <article className="flex min-h-[196px] flex-col rounded-[28px] bg-white p-[22px] text-[#1a1e24]">
                <p className="mb-3 flex items-center gap-2.5 text-[15px]">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="#1a1e24"
                    strokeWidth="1.5"
                    aria-hidden="true"
                  >
                    <circle cx="6" cy="6" r="2.5" />
                    <circle cx="14" cy="6" r="2.5" />
                    <circle cx="10" cy="14" r="2.5" />
                  </svg>
                  Unemployment
                </p>

                <p className="text-[46px] font-medium leading-none tracking-[-0.02em]">
                  <CountUp
                    value={
                      overview.unemployment
                        .rate_percent
                    }
                    format={(value) =>
                      formatPercent(value)
                    }
                  />
                </p>

                <p className="mt-1 text-[13px] text-[#6b6f72]">
                  model-based estimate
                </p>

                <span className="mt-2 w-fit rounded-full bg-[#ebebe5] px-3 py-1 text-[11px] text-[#6b6f72]">
                  Model-based
                </span>

                <p className="mt-auto border-t border-[#e8e8e2] pt-[9px] text-[11px] text-[#6b6f72]">
                  Reference period: {formatDate(
                    overview.unemployment
                      .reference_period,
                  )}
                </p>
              </article>
            )}
          </section>

          <ExploreLowerSection
            rentHistory={rentHistory}
            locationName={
              overview.location.name
            }
            overview={overview}
            region={
              overview.location
                .region_or_country
            }
            latitude={
              coordinates?.latitude
            }
            longitude={
              coordinates?.longitude
            }
          />
        </>
      )}
    </>
  );
}
