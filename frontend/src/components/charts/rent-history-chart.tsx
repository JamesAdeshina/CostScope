"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  MetricHistoryResponse,
} from "@/types/api";


interface RentHistoryChartProps {
  history: MetricHistoryResponse;
}


function toDate(
  value: string,
): Date {
  return new Date(
    `${value}T00:00:00`,
  );
}


function formatMonth(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    "en-GB",
    {
      month: "short",
      year: "numeric",
    },
  ).format(
    toDate(value),
  );
}


function formatYear(
  value: string,
): string {
  return String(
    toDate(value).getFullYear(),
  );
}


function formatCurrency(
  value: number,
): string {
  return new Intl.NumberFormat(
    "en-GB",
    {
      style: "currency",
      currency: "GBP",
      maximumFractionDigits: 0,
    },
  ).format(value);
}


export function RentHistoryChart({
  history,
}: RentHistoryChartProps) {
  const observations =
    history.observations;

  if (
    observations.length === 0
  ) {
    return null;
  }


  /*
   * Show one x-axis label per year.
   * We pick January where available.
   */
  const yearTicks =
    observations
      .filter(
        (observation) =>
          toDate(
            observation.reference_period,
          ).getMonth() === 0,
      )
      .map(
        (observation) =>
          observation.reference_period,
      );


  /*
   * Always include the first point
   * if the history does not begin in
   * January.
   */
  const first =
    observations[0];

  if (
    !yearTicks.includes(
      first.reference_period,
    )
  ) {
    yearTicks.unshift(
      first.reference_period,
    );
  }


  const lastIndex =
    observations.length - 1;


  /*
   * Give the chart a sensible,
   * slightly padded vertical range.
   *
   * This avoids the huge amount of
   * empty space we were seeing.
   */
  const values =
    observations.map(
      (observation) =>
        observation.value,
    );

  const minimum =
    Math.min(...values);

  const maximum =
    Math.max(...values);

  const lowerBound =
    Math.max(
      0,
      Math.floor(
        (minimum - 75) /
          100,
      ) * 100,
    );

  const upperBound =
    Math.ceil(
      (maximum + 75) /
        100,
    ) * 100;


  const reduceMotion =
    typeof window !==
      "undefined" &&
    window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;


  return (
    <div
      className="h-[245px] w-full"
      role="img"
      aria-label="Average monthly private rent over time"
    >
      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <LineChart
          data={observations}
          margin={{
            top: 12,
            right: 10,
            bottom: 4,
            left: 4,
          }}
        >
          <CartesianGrid
            vertical={false}
            stroke="#e7e8e3"
            strokeWidth={1}
          />

          <XAxis
            dataKey="reference_period"
            ticks={yearTicks}
            tickFormatter={
              formatYear
            }
            interval={
              "preserveStartEnd"
            }
            minTickGap={24}
            tick={{
              fontSize: 11,
              fill: "#6b6f72",
              fontWeight: 400,
            }}
            tickMargin={10}
            axisLine={false}
            tickLine={false}
          />

          <YAxis
            domain={[
              lowerBound,
              upperBound,
            ]}
            tickCount={5}
            allowDecimals={false}
            tickFormatter={(
              value: number,
            ) =>
              `£${value.toLocaleString(
                "en-GB",
              )}`
            }
            width={60}
            tick={{
              fontSize: 11,
              fill: "#6b6f72",
              fontWeight: 400,
            }}
            tickMargin={8}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            cursor={{
              stroke: "#d8d9d4",
              strokeWidth: 1,
              strokeDasharray:
                "4 4",
            }}
            labelFormatter={(
              value,
            ) =>
              formatMonth(
                String(value),
              )
            }
            formatter={(
              value,
            ) => [
              formatCurrency(
                Number(value),
              ),
              "Monthly rent",
            ]}
            contentStyle={{
              background:
                "#1a1e24",
              border: "none",
              borderRadius:
                "10px",
              padding:
                "10px 12px",
              boxShadow:
                "0 10px 30px rgba(26,30,36,.18)",
              color: "#ffffff",
              fontSize: "12px",
            }}
            labelStyle={{
              color: "#b9bdc1",
              marginBottom:
                "4px",
            }}
            itemStyle={{
              color: "#ffffff",
            }}
          />

          <Line
            type="monotone"
            dataKey="value"
            stroke="#0a84ff"
            strokeWidth={3}
            strokeLinecap="round"
            strokeLinejoin="round"
            isAnimationActive={
              !reduceMotion
            }
            animationDuration={
              1600
            }
            animationEasing="ease-out"
            dot={(props: {
              cx?: number;
              cy?: number;
              index?: number;
            }) =>
              props.index ===
              lastIndex ? (
                <circle
                  key="end-dot"
                  cx={
                    props.cx
                  }
                  cy={
                    props.cy
                  }
                  r={5.5}
                  fill="#0a84ff"
                  stroke="#ffffff"
                  strokeWidth={2}
                />
              ) : (
                <g
                  key={`dot-${props.index}`}
                />
              )
            }
            activeDot={{
              r: 5,
              fill: "#0a84ff",
              stroke:
                "#ffffff",
              strokeWidth: 2,
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}