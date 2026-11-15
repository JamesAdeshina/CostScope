"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  getLocationOverview,
  searchLocations,
} from "@/lib/api/client";

import {
  formatCurrency,
  formatPercent,
} from "@/lib/formatters";

import type {
  LocationOverviewResponse,
  LocationSearchResult,
} from "@/types/api";


interface LocationCompareProps {
  primary: LocationOverviewResponse;
  onClose: () => void;
}


const METRICS: {
  label: string;
  read: (
    overview: LocationOverviewResponse,
  ) => string | null;
}[] = [
  {
    label: "Average private rent",
    read: (o) =>
      o.rent
        ? formatCurrency(
            o.rent.monthly_rent,
          )
        : null,
  },
  {
    label: "Annual rent change",
    read: (o) =>
      o.rent
        ? formatPercent(
            o.rent
              .annual_change_percent,
            2,
          )
        : null,
  },
  {
    label: "Median annual earnings",
    read: (o) =>
      o.earnings
        ? formatCurrency(
            o.earnings
              .median_annual_pay,
          )
        : null,
  },
  {
    label: "Unemployment",
    read: (o) =>
      o.unemployment
        ? formatPercent(
            o.unemployment
              .rate_percent,
          )
        : null,
  },
];


function CompareSlot({
  index,
  onChange,
}: {
  index: number;
  onChange: (
    overview: LocationOverviewResponse | null,
  ) => void;
}) {
  const [query, setQuery] =
    useState("");

  const [selected, setSelected] =
    useState<LocationSearchResult | null>(
      null,
    );

  const [
    suggestions,
    setSuggestions,
  ] = useState<
    LocationSearchResult[]
  >([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(
      null,
    );

  useEffect(() => {
    const value = query.trim();

    if (
      value.length < 2 ||
      selected
    ) {
      setSuggestions([]);

      return;
    }

    const timeout =
      window.setTimeout(
        async () => {
          try {
            const results =
              await searchLocations(
                value,
              );

            setSuggestions(
              results.slice(0, 6),
            );
          } catch {
            setSuggestions([]);
          }
        },
        250,
      );

    return () =>
      window.clearTimeout(
        timeout,
      );
  }, [query, selected]);

  async function choose(
    location: LocationSearchResult,
  ) {
    setSelected(location);
    setQuery(location.name);
    setSuggestions([]);
    setLoading(true);
    setError(null);

    try {
      onChange(
        await getLocationOverview(
          location.location_code,
        ),
      );
    } catch (requestError) {
      onChange(null);

      setError(
        requestError instanceof
          Error
          ? requestError.message
          : "Unable to load this location.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleChange(
    value: string,
  ) {
    setQuery(value);
    setError(null);

    if (selected) {
      setSelected(null);
      onChange(null);
    } else if (!value) {
      onChange(null);
    }
  }

  return (
    <div className="relative mb-3">
      <input
        type="text"
        value={query}
        onChange={(event) =>
          handleChange(
            event.target.value,
          )
        }
        aria-label={`Location ${index + 2}`}
        autoComplete="off"
        placeholder="Add a location"
        className="block w-full rounded-2xl border-0 bg-[#ebebe5] py-4 pl-5 pr-11 text-base text-[#1a1e24] outline-none transition-colors placeholder:text-[#6b6f72]"
      />

      <svg
        width="12"
        height="8"
        viewBox="0 0 12 8"
        fill="none"
        stroke="#1a1e24"
        strokeWidth="1.6"
        className="pointer-events-none absolute right-[18px] top-1/2 -translate-y-1/2"
        aria-hidden="true"
      >
        <path d="m1 1 5 5 5-5" />
      </svg>

      {loading && (
        <p className="mt-1.5 text-xs text-[#6b6f72]">
          Loading…
        </p>
      )}

      {error && (
        <p
          role="alert"
          className="mt-1.5 text-xs text-red-800"
        >
          {error}
        </p>
      )}

      {suggestions.length > 0 && (
        <div className="absolute left-0 right-0 top-[58px] z-40 overflow-hidden rounded-2xl border border-[#e4e4dd] bg-white shadow-[0_18px_50px_rgba(26,30,36,.12)]">
          {suggestions.map(
            (location) => (
              <button
                key={
                  location.location_code
                }
                type="button"
                onClick={() =>
                  void choose(
                    location,
                  )
                }
                className="flex w-full flex-col items-start border-b border-[#eeeeea] bg-white px-5 py-3 text-left transition last:border-0 hover:bg-[#f6f6f2]"
              >
                <span className="text-sm font-medium text-[#1a1e24]">
                  {location.name}
                </span>

                {location.region_or_country && (
                  <span className="text-xs text-[#6b6f72]">
                    {
                      location.region_or_country
                    }
                  </span>
                )}
              </button>
            ),
          )}
        </div>
      )}
    </div>
  );
}


export function LocationCompare({
  primary,
  onClose,
}: LocationCompareProps) {
  const [others, setOthers] =
    useState<
      (LocationOverviewResponse | null)[]
    >([null, null]);

  function setOther(
    slot: number,
    overview: LocationOverviewResponse | null,
  ) {
    setOthers((current) =>
      current.map((item, i) =>
        i === slot
          ? overview
          : item,
      ),
    );
  }

  const columns = [
    primary,
    ...others.filter(
      (
        item,
      ): item is LocationOverviewResponse =>
        item !== null,
    ),
  ];

  return (
    <section className="cs-rise mt-[18px] grid gap-[30px] rounded-[28px] bg-white p-[26px] text-[#1a1e24] min-[1001px]:grid-cols-[0.8fr_2fr]">
      <div>
        <h2 className="text-[28px] font-medium">
          Compare locations
        </h2>

        <p className="mb-[22px] mt-1.5 text-sm text-[#6b6f72]">
          Explore the cost of living across UK areas.
        </p>

        <div
          aria-label="Location 1"
          className="mb-3 rounded-2xl bg-[#e8ef7a] px-5 py-4 text-base"
        >
          {primary.location.name}
        </div>

        <CompareSlot
          index={0}
          onChange={(overview) =>
            setOther(0, overview)
          }
        />

        <CompareSlot
          index={1}
          onChange={(overview) =>
            setOther(1, overview)
          }
        />

        <button
          type="button"
          onClick={onClose}
          className="group mt-1.5 inline-flex items-center gap-2.5 rounded-full bg-[#ebebe5] px-[22px] py-[13px] text-sm font-medium text-[#1a1e24] transition hover:bg-[#dededa] active:scale-[0.97]"
        >
          Hide comparison
        </button>
      </div>

      <div className="min-w-0 overflow-x-auto">
        <table className="w-full border-collapse text-[15px]">
          <thead>
            <tr>
              <th className="bg-[#ebebe5] px-5 py-[14px] text-left font-medium">
                Metric
              </th>

              {columns.map(
                (column, i) => (
                  <th
                    key={
                      column.location
                        .location_code
                    }
                    className={`px-5 py-[14px] text-left font-medium ${
                      i === 0
                        ? "bg-[#e8ef7a]"
                        : "bg-[#ebebe5]"
                    }`}
                  >
                    {
                      column.location
                        .name
                    }
                  </th>
                ),
              )}
            </tr>
          </thead>

          <tbody>
            {METRICS.map(
              (metric) => (
                <tr
                  key={metric.label}
                >
                  <td className="border-b border-[#e8e8e2] px-5 py-[14px] text-[#6b6f72]">
                    {metric.label}
                  </td>

                  {columns.map(
                    (column, i) => {
                      const value =
                        metric.read(
                          column,
                        ) ?? "—";

                      return (
                        <td
                          key={`${column.location.location_code}-${value}`}
                          className={`cs-flash border-b border-[#e8e8e2] px-5 py-[14px] transition-colors duration-300 ${
                            i === 0
                              ? "bg-[#f4f7d0]"
                              : ""
                          }`}
                        >
                          {value}
                        </td>
                      );
                    },
                  )}
                </tr>
              ),
            )}
          </tbody>
        </table>

        {columns.length === 1 && (
          <p className="mt-3 text-[13px] text-[#6b6f72]">
            Add up to two more locations to compare them side by side.
          </p>
        )}
      </div>
    </section>
  );
}
