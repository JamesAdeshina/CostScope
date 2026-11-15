import Link from "next/link";

import {
  SiteFooter,
} from "@/components/layout/site-footer";

import {
  SiteHeader,
} from "@/components/layout/site-header";

import {
  UkMap,
} from "@/components/maps/uk-map";


const steps = [
  {
    number: "01",
    title: "Find your area",
    body: "Search a city, town or postcode to see the local picture, with UK context alongside it.",
  },
  {
    number: "02",
    title: "Compare your shortlist",
    body: "Bring up to three locations together. Look beyond one number to the trade-offs that matter.",
  },
  {
    number: "03",
    title: "See where it comes from",
    body: "Check source definitions and reference periods. Every indicator needs a little context.",
  },
];


const principles = [
  {
    title:
      "Official sources, clearly credited",
    body:
      "Start with published statistics and keep the source visible.",
  },
  {
    title:
      "Local figures. National context.",
    body:
      "Separate local measures from UK-wide indicators such as inflation.",
  },
  {
    title:
      "Different dates, made visible",
    body:
      "Show each reference period rather than imply everything is current at once.",
  },
  {
    title:
      "A starting point, not a personal budget",
    body:
      "Area-level averages cannot capture every household or every street.",
  },
];


export default function AboutPage() {
  return (
    <main className="min-h-screen bg-[#f3f3ee] text-[#1a1e24]">
      <div className="mx-auto max-w-[1536px] px-[18px] min-[1001px]:px-10">
        <SiteHeader active="about" />

        <section className="grid items-start gap-10 min-[1001px]:grid-cols-[1.25fr_1fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.02em] text-[#6b6f72]">
              About CostScope
            </p>

            <h1 className="mb-[22px] mt-[14px] text-[clamp(44px,6vw,72px)] font-normal leading-[1.05] tracking-[-0.02em] text-[#1a1e24]">
              Local living.
              <br />
              A little clearer.
            </h1>

            <p className="max-w-[760px] text-lg leading-[1.45] text-[#6b6f72]">
              Big decisions start with a better picture. CostScope brings local rent, earnings and economic indicators into one place, so you can explore an area or compare your next move.
            </p>

            <p className="mt-[22px] text-sm text-[#1a1e24]">
              Less searching. More understanding.
            </p>
          </div>

<article className="relative min-h-[260px] overflow-hidden rounded-[28px] bg-[#e8ef7a] px-7 py-[26px] text-[#1a1e24]">
  <div className="relative z-10 max-w-[58%]">
    <h2 className="text-[44px] font-normal leading-[1.1] tracking-[-0.02em] text-[#1a1e24]">
      Local detail.
      <br />
      National context.
    </h2>

    <p className="mt-[34px] max-w-[260px] text-[15px] leading-6 text-[#1a1e24]">
      One place to understand
      <br />
      the bigger picture.
    </p>

    <span className="mt-7 inline-flex rounded-full bg-[#1a1e24] px-5 py-[11px] text-sm font-medium text-white">
      Built for everyday decisions
    </span>
  </div>

  <div className="absolute bottom-[18px] right-[24px] top-[18px] z-0 w-[42%] opacity-70">
    <UkMap
      latitude={52.922}
      longitude={-1.476}
      region="East Midlands"
      locationName="Derby"
      className="h-full w-full"
    />
  </div>
</article>
        </section>

        <section className="mt-[34px]">
          <h2 className="text-[30px] font-normal tracking-[-0.01em] text-[#1a1e24]">
            From a postcode to a perspective.
          </h2>

          <p className="mt-1 text-sm text-[#6b6f72]">
            A simple way to make sense of the places that matter to you.
          </p>

          <div className="mt-4 grid gap-6 min-[1001px]:grid-cols-3">
            {steps.map((step) => (
              <article
                key={step.number}
                className="min-h-[195px] rounded-[28px] bg-white p-[22px]"
              >
                <span className="text-xs text-[#6b6f72]">
                  {step.number}
                </span>

                <h3 className="mb-[10px] mt-[14px] text-[24px] font-normal text-[#1a1e24]">
                  {step.title}
                </h3>

                <p className="text-[15px] text-[#6b6f72]">
                  {step.body}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-[30px] grid gap-10 min-[1001px]:grid-cols-[1fr_1.6fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.02em] text-[#6b6f72]">
              Our approach
            </p>

            <h2 className="mb-[22px] mt-[14px] text-[42px] font-normal leading-[1.1] tracking-[-0.01em] text-[#1a1e24]">
              Clarity, without
              <br />
              the shortcuts.
            </h2>

            <p className="max-w-[760px] text-[17px] leading-[1.45] text-[#6b6f72]">
              A useful comparison is an informed one. Here is what we keep in view.
            </p>
          </div>

          <div>
            {principles.map((item) => (
              <article
                key={item.title}
                className="border-b border-[#dcdcd5] py-[18px] first:pt-0"
              >
                <h3 className="text-[19px] font-normal text-[#1a1e24]">
                  {item.title}
                </h3>

                <p className="text-sm text-[#6b6f72]">
                  {item.body}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-[34px] flex flex-col items-start gap-5 rounded-[28px] bg-[#1a1e24] px-8 py-[30px] text-white min-[1001px]:flex-row min-[1001px]:items-center min-[1001px]:justify-between">
          <div>
            <h2 className="text-[36px] font-normal tracking-[-0.01em] text-white">
              Your next move, in context.
            </h2>

            <p className="mt-5 text-[#b9bdc1]">
              Explore your area or see how your shortlist compares.
            </p>
          </div>

          <Link
            href="/"
            className="flex min-w-[310px] items-center justify-between rounded-full bg-[#e8ef7a] px-[26px] py-[18px] text-base font-medium text-[#1a1e24] transition hover:-translate-y-px hover:bg-[#dfe86a] active:scale-[0.97]"
          >
            Explore locations
            <span>→</span>
          </Link>
        </section>

        <SiteFooter />
      </div>
    </main>
  );
}
