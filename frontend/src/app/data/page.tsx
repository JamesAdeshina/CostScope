import {
  SiteFooter,
} from "@/components/layout/site-footer";

import {
  SiteHeader,
} from "@/components/layout/site-header";


const sourceRows = [
  {
    indicator: "Average private rent",
    source: "Price Index of Private Rents",
    geography: "Local authority",
    period: "Aug 2026",
    publisher: "ONS",
    href: "https://www.ons.gov.uk/",
  },
  {
    indicator: "Median annual earnings",
    source: "Annual Survey of Hours and Earnings",
    geography: "Local authority",
    period: "Apr 2025",
    publisher: "ONS",
    href: "https://www.ons.gov.uk/",
  },
  {
    indicator: "UK inflation",
    source: "Consumer Prices Index",
    geography: "United Kingdom",
    period: "Sep 2026",
    publisher: "ONS",
    href: "https://www.ons.gov.uk/",
  },
  {
    indicator: "Unemployment",
    source: "Model-based unemployment estimates",
    geography: "Local authority",
    period: "Mar 2026",
    publisher: "Nomis",
    href: "https://www.nomisweb.co.uk/",
  },
];


export default function DataPage() {
  return (
    <main className="min-h-screen bg-[#f3f3ee] text-[#1a1e24]">
      <div className="mx-auto max-w-[1536px] px-[18px] min-[1001px]:px-10">
        <SiteHeader active="data" />

        <section className="grid items-start gap-10 min-[1001px]:grid-cols-[1.6fr_1fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.02em] text-[#6b6f72]">
              Sources &amp; methodology
            </p>

            <h1 className="mb-[22px] mt-[14px] text-[clamp(44px,6vw,72px)] font-normal leading-[1.05] tracking-[-0.02em] text-[#1a1e24]">
              The data behind
              <br />
              the detail.
            </h1>

            <p className="max-w-[760px] text-lg leading-[1.45] text-[#6b6f72]">
              Know what you are comparing. Find the sources, reference periods and context behind the numbers in CostScope.
            </p>
          </div>

          <article className="rounded-[28px] bg-[#ebebe5] px-[26px] py-6 text-[#1a1e24]">
            <p className="text-xs uppercase tracking-[0.02em] text-[#6b6f72]">
              A note on timing
            </p>

            <h2 className="mb-[18px] mt-[22px] text-[31px] font-normal leading-[1.2] tracking-[-0.01em] text-[#1a1e24]">
              Not every number
              <br />
              has the same date.
            </h2>

            <p className="text-[15px] text-[#6b6f72]">
              Each indicator shows its own reference period. Different surveys and releases follow different schedules.
            </p>
          </article>
        </section>

        <section className="mt-[34px]">
          <h2 className="text-[30px] font-normal tracking-[-0.01em] text-[#1a1e24]">
            Sources at a glance
          </h2>

          <p className="mt-1 text-sm text-[#6b6f72]">
            Published by the Office for National Statistics and Nomis. Periods below match the indicators shown in Explore.
          </p>

          <div className="mt-[18px] overflow-x-auto rounded-[28px] bg-white">
            <table className="w-full min-w-[760px] border-collapse text-[15px] text-[#1a1e24]">
              <thead>
                <tr className="bg-[#ebebe5] text-left">
                  <th className="px-6 py-[15px] text-xs font-medium text-[#6b6f72]">
                    Indicator
                  </th>
                  <th className="px-6 py-[15px] text-xs font-medium text-[#6b6f72]">
                    Published source
                  </th>
                  <th className="px-6 py-[15px] text-xs font-medium text-[#6b6f72]">
                    Geography
                  </th>
                  <th className="px-6 py-[15px] text-xs font-medium text-[#6b6f72]">
                    Reference period
                  </th>
                  <th className="px-6 py-[15px] text-xs font-medium text-[#6b6f72]">
                    Source
                  </th>
                </tr>
              </thead>

              <tbody>
                {sourceRows.map((row) => (
                  <tr
                    key={row.indicator}
                    className="border-b border-[#eeeeea] transition-colors duration-200 last:border-0 hover:bg-[#fafaf6]"
                  >
                    <td className="px-6 py-5">
                      {row.indicator}
                    </td>

                    <td className="px-6 py-5">
                      {row.source}
                    </td>

                    <td className="px-6 py-5 text-[#6b6f72]">
                      {row.geography}
                    </td>

                    <td className="px-6 py-5">
                      {row.period}
                    </td>

                    <td className="px-6 py-5">
                      <a
                        href={row.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-[#1a1e24]"
                      >
                        {row.publisher} ↗
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="mt-[14px] text-[13px] text-[#6b6f72]">
            Reference period = the time the figure describes, not necessarily the date it was published.
          </p>
        </section>

        <section className="mt-[26px] grid gap-10 rounded-[28px] bg-white p-7 min-[1001px]:grid-cols-[1fr_1.3fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.02em] text-[#6b6f72]">
              Understanding the index
            </p>

            <h2 className="my-[14px] text-[30px] font-normal tracking-[-0.01em] text-[#1a1e24]">
              One view. Several moving parts.
            </h2>

            <p className="text-[15px] text-[#6b6f72]">
              The Cost of Living Index is planned as a CostScope composite combining housing, energy, transport, consumer prices and income into a relative summary. It is not currently used as a production metric.
            </p>

            <p className="mt-[50px]">
              <span className="inline-block rounded-full bg-[#e8ef7a] px-5 py-[11px] text-sm font-medium text-[#1a1e24]">
                Methodology in development
              </span>{" "}
              <small className="ml-1 text-[#6b6f72]">
                CostScope composite
              </small>
            </p>
          </div>

          <div>
            <div className="grid gap-4 min-[561px]:grid-cols-3">
              <div className="rounded-[18px] bg-[#ebebe5] px-[18px] pb-4 pt-[18px] text-[23px]">
                Below 100
                <small className="mt-2 block text-[13px] text-[#6b6f72]">
                  Lower relative cost
                </small>
              </div>

              <div className="rounded-[18px] bg-[#e8ef7a] px-[18px] pb-4 pt-[18px] text-[23px]">
                100
                <small className="mt-2 block text-[13px] text-[#1a1e24]">
                  UK baseline
                </small>
              </div>

              <div className="rounded-[18px] bg-[#ebebe5] px-[18px] pb-4 pt-[18px] text-[23px]">
                Above 100
                <small className="mt-2 block text-[13px] text-[#6b6f72]">
                  Higher relative cost
                </small>
              </div>
            </div>

            <h3 className="mb-2.5 mt-[26px] text-lg font-medium text-[#1a1e24]">
              A CostScope composite, not an ONS statistic.
            </h3>

            <p className="text-[15px] text-[#6b6f72]">
              Use the index alongside the underlying measures. A lower score does not mean every category is cheaper, and it is not a forecast of your personal spending. We will publish the weighting and calculation methodology before this becomes an active production metric.
            </p>
          </div>
        </section>

        <section className="mt-[34px]">
          <h2 className="text-[30px] font-normal tracking-[-0.01em] text-[#1a1e24]">
            Read the numbers in context.
          </h2>

          <div className="mt-4 grid gap-[18px] min-[1001px]:grid-cols-3">
            <article className="min-h-[146px] rounded-[22px] bg-[#ebebe5] p-[22px]">
              <h3 className="mb-3 text-[20px] font-normal text-[#1a1e24]">
                Averages are not individual budgets
              </h3>

              <p className="text-[15px] text-[#6b6f72]">
                Your rent, earnings and household costs may differ from the area-level picture.
              </p>
            </article>

            <article className="min-h-[146px] rounded-[22px] bg-[#ebebe5] p-[22px]">
              <h3 className="mb-3 text-[20px] font-normal text-[#1a1e24]">
                Local and national are different
              </h3>

              <p className="text-[15px] text-[#6b6f72]">
                UK inflation provides context. It is not a city-specific inflation rate.
              </p>
            </article>

            <article className="min-h-[146px] rounded-[22px] bg-[#ebebe5] p-[22px]">
              <h3 className="mb-3 text-[20px] font-normal text-[#1a1e24]">
                Compare like with like
              </h3>

              <p className="text-[15px] text-[#6b6f72]">
                Check the geography, definition and reference period before drawing conclusions.
              </p>
            </article>
          </div>
        </section>

        <SiteFooter />
      </div>
    </main>
  );
}
