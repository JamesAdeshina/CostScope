// src/components/explore/cost-of-living-index.tsx

"use client";

import {
  useEffect,
  useState,
} from "react";


/*
 * Single source of truth: the ring segments, the legend dots,
 * the headline number and the aria-label are all derived from this.
 * Each category has its own colour, so the legend can be read
 * against the ring.
 */
const breakdown = [
  {
    label: "Housing",
    weight: 32,
    score: 102.3,
    color: "#1a1e24",
  },
  {
    label: "Energy",
    weight: 18,
    score: 96.1,
    color: "#18c39e",
  },
  {
    label: "Transport",
    weight: 15,
    score: 108.7,
    color: "#ff7f1f",
  },
  {
    label: "Consumer prices",
    weight: 15,
    score: 97.6,
    color: "#e8ef63",
  },
  {
    label: "Income",
    weight: 20,
    score: 89.8,
    color: "#0a3fd1",
  },
];


/* Weighted average of the category scores (UK = 100). */
const indexValue = breakdown.reduce(
  (sum, item) =>
    sum +
    (item.weight / 100) * item.score,
  0,
);


const RADIUS = 72;
const STROKE = 18;
const CIRCUMFERENCE =
  2 * Math.PI * RADIUS;

/* Visible gap between neighbouring segments (round caps add STROKE). */
const GAP = 3;


export function CostOfLivingIndex() {
  const [drawn, setDrawn] =
    useState(false);

  /* Rings draw in on mount, like the donut in costscope.html. */
  useEffect(() => {
    const frame =
      requestAnimationFrame(() =>
        setDrawn(true),
      );

    return () =>
      cancelAnimationFrame(frame);
  }, []);


  let cursor = 0;

  const segments = breakdown.map(
    (item) => {
      const length =
        (item.weight / 100) *
        CIRCUMFERENCE;

      const start = cursor;

      cursor += length;

      /*
       * Round caps extend each dash by STROKE / 2 at both ends, so the
       * drawn dash is shortened by STROKE + GAP and nudged forward by
       * half of that to keep the segment centred in its slot.
       */
      const dash = Math.max(
        length - STROKE - GAP,
        0.01,
      );

      const offset =
        start + (STROKE + GAP) / 2;

      return {
        ...item,
        dash,
        offset,
      };
    },
  );


  return (
    <article className="@container flex h-full min-h-[310px] flex-col overflow-hidden rounded-[28px] bg-white p-[22px] text-[#1a1e24]">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="flex shrink-0 items-start justify-between gap-4">
        <div className="min-w-0">
          <h2 className="text-[24px] font-medium leading-[1.1] tracking-[-0.02em] text-[#1a1e24]">
            Cost of Living Index
          </h2>

          <p className="mt-1.5 max-w-[340px] text-[12px] leading-[1.45] text-[#6b6f72]">
            A composite measure based on housing, energy,
            transport, consumer prices and income.
          </p>
        </div>

        <span className="inline-flex shrink-0 items-center gap-2 rounded-full bg-[#d8f5e6] px-3 py-1 text-[10px] font-medium text-[#148763]">
          <span className="h-2 w-2 rounded-full bg-[#18c39e]" />

          Medium
        </span>
      </div>


      {/* =====================================================
          INDEX + BREAKDOWN
          Narrow card: the breakdown hugs its content and the donut
          takes all remaining space (up to 240px).
          Wide card: the columns split and the score column appears
          (container queries).
          ===================================================== */}

      <div className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_max-content] items-center gap-4 pt-3 @[500px]:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] @[760px]:gap-7">

        {/* ===================================================
            DONUT
            =================================================== */}

        <div className="flex min-w-0 items-center justify-center">
          <svg
            viewBox="0 0 200 200"
            role="img"
            aria-label={`Cost of Living Index score ${indexValue.toFixed(1)}, United Kingdom baseline 100`}
            className="h-auto w-full max-w-[240px] overflow-visible"
          >
            <g
              fill="none"
              strokeWidth={STROKE}
              strokeLinecap="round"
              transform="rotate(-90 100 100)"
            >
              {/* Track */}
              <circle
                cx="100"
                cy="100"
                r={RADIUS}
                stroke="#eef3f8"
              />

              {segments.map(
                (segment) => (
                  <circle
                    key={segment.label}
                    cx="100"
                    cy="100"
                    r={RADIUS}
                    stroke={
                      segment.color
                    }
                    strokeDasharray={`${
                      drawn
                        ? segment.dash
                        : 0.01
                    } ${CIRCUMFERENCE}`}
                    strokeDashoffset={
                      -segment.offset
                    }
                    style={{
                      transition:
                        "stroke-dasharray 1.2s cubic-bezier(.4,0,.2,1)",
                    }}
                  />
                ),
              )}
            </g>

            <text
              x="100"
              y="99"
              textAnchor="middle"
              fill="#0a347f"
              fontSize="40"
              fontWeight="600"
              letterSpacing="-1.2"
            >
              {indexValue.toFixed(1)}
            </text>

            <text
              x="100"
              y="128"
              textAnchor="middle"
              fill="#3971c6"
              fontSize="15"
              fontWeight="400"
            >
              UK = 100
            </text>
          </svg>
        </div>


        {/* ===================================================
            BREAKDOWN
            =================================================== */}

        <div className="min-w-0 self-center">
          <h3 className="mb-1.5 text-[13px] font-semibold leading-4 text-[#0a347f]">
            Breakdown
          </h3>

          <div className="w-max max-w-full @[500px]:w-full">
            {breakdown.map(
              (item) => (
                <div
                  key={item.label}
                  className="grid grid-cols-[12px_minmax(0,1fr)] items-start gap-x-2.5 border-b border-[#d6e5f3] py-[5px] last:border-b-0 @[500px]:grid-cols-[12px_minmax(0,1fr)_auto]"
                >
                  {/* colour marker, aligned to the first text line */}

                  <span
                    className="mt-[2px] h-[10px] w-[10px] rounded-full shadow-[inset_0_0_0_1px_rgba(26,30,36,.12)]"
                    style={{
                      backgroundColor:
                        item.color,
                    }}
                    aria-hidden="true"
                  />


                  {/* label + weighting */}

                  <div className="min-w-0">
                    <p className="whitespace-normal break-words text-[11px] leading-[13px] text-[#3971c6]">
                      {item.label}
                    </p>

                    <p className="mt-[1px] text-[10px] leading-[11px] text-[#3971c6]">
                      {item.weight}%
                    </p>
                  </div>


                  {/* Score only when the CARD itself is wide */}

                  <span className="hidden whitespace-nowrap pl-3 pt-[1px] text-[10px] font-semibold text-[#0a347f] @[500px]:block">
                    {item.score.toFixed(1)}
                  </span>
                </div>
              ),
            )}
          </div>
        </div>
      </div>
    </article>
  );
}