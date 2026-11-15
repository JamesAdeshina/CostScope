"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";


const sources = [
  {
    category: "Housing",
    title: "Private rents",
    description:
      "Price Index of Private Rents, UK: monthly price statistics",
    code: "ONS_PIPR",
    href: "https://www.ons.gov.uk/",
  },
  {
    category: "Income",
    title: "Pay & earnings",
    description:
      "Earnings and hours worked, place of residence by local authority: ASHE Table 8",
    code: "ONS_ASHE",
    href: "https://www.ons.gov.uk/",
  },
  {
    category: "Prices",
    title: "Consumer prices",
    description:
      "Consumer price inflation time series",
    code: "ONS_CPI_MM23",
    href: "https://www.ons.gov.uk/",
  },
  {
    category: "Employment",
    title: "Labour market",
    description:
      "Model-based estimates of unemployment from Nomis",
    code: "NOMIS_UNEMPLOYMENT_MODEL",
    href: "https://www.nomisweb.co.uk/",
  },
];


export function OfficialSources() {
  const [open, setOpen] =
    useState(false);

  const closeRef =
    useRef<HTMLButtonElement>(null);

  const lastFocus =
    useRef<HTMLElement | null>(
      null,
    );


  function openModal() {
    lastFocus.current =
      document.activeElement as HTMLElement | null;

    setOpen(true);

    window.setTimeout(
      () =>
        closeRef.current?.focus(),
      50,
    );
  }


  function closeModal() {
    setOpen(false);

    lastFocus.current?.focus();
  }


  useEffect(() => {
    if (!open) {
      return;
    }

    function handleKeyDown(
      event: KeyboardEvent,
    ) {
      if (event.key === "Escape") {
        setOpen(false);

        lastFocus.current?.focus();
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () =>
      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
  }, [open]);


  return (
    <>
      <section className="mt-[18px] flex flex-col gap-3 rounded-[28px] bg-white px-6 py-[18px] min-[561px]:flex-row min-[561px]:items-center">
        <div className="flex min-w-0 items-center gap-4">
          <svg
            width="26"
            height="26"
            viewBox="0 0 26 26"
            fill="none"
            stroke="#6b6f72"
            strokeWidth="1.5"
            className="shrink-0"
            aria-hidden="true"
          >
            <circle
              cx="13"
              cy="13"
              r="10"
            />
            <path d="M13 8v6M13 17v1" />
          </svg>

          <div>
            <h2 className="text-[20px] font-medium text-[#1a1e24]">
              Built on official data
            </h2>

            <p className="text-[13px] text-[#6b6f72]">
              Transparent sources. No guesswork.
            </p>
          </div>
        </div>

        <p className="text-sm text-[#6b6f72] min-[561px]:ml-auto min-[561px]:mr-10">
          ONS · Nomis
        </p>

        <button
          type="button"
          onClick={openModal}
          aria-haspopup="dialog"
          className="group inline-flex items-center justify-center gap-2 rounded-full bg-[#ebebe5] px-[22px] py-[13px] text-sm font-medium text-[#1a1e24] transition hover:bg-[#dededa] active:scale-[0.97]"
        >
          View sources

          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            className="transition-transform duration-200 group-hover:translate-x-[3px]"
            aria-hidden="true"
          >
            <path d="m5 2 5 5-5 5" />
          </svg>
        </button>
      </section>

      <div
        aria-hidden={!open}
        className={`fixed inset-0 z-[100] flex items-center justify-center bg-[rgba(26,30,36,.45)] p-5 backdrop-blur-[3px] transition-[opacity,visibility] duration-300 ${
          open
            ? "visible opacity-100"
            : "invisible opacity-0"
        }`}
        onMouseDown={(event) => {
          if (
            event.target ===
            event.currentTarget
          ) {
            closeModal();
          }
        }}
      >
        <section
          role="dialog"
          aria-modal="true"
          aria-labelledby="sources-title"
          className={`max-h-[90vh] w-full max-w-[1200px] overflow-y-auto rounded-[28px] bg-[#f3f3ee] px-6 py-7 text-[#1a1e24] transition-transform duration-[400ms] ease-[cubic-bezier(.2,.8,.2,1)] min-[561px]:px-[34px] min-[561px]:py-[30px] ${
            open
              ? "[transform:none]"
              : "[transform:translateY(24px)_scale(.97)]"
          }`}
        >
          <header className="flex flex-wrap items-center gap-[14px]">
            <h2
              id="sources-title"
              className="flex items-center gap-[14px] text-[28px] font-medium"
            >
              <svg
                width="28"
                height="28"
                viewBox="0 0 32 32"
                fill="none"
                stroke="#1a1e24"
                strokeWidth="1.8"
                aria-hidden="true"
              >
                <circle cx="5" cy="16" r="2.5" />
                <circle cx="20" cy="5" r="2.5" />
                <circle cx="26" cy="16" r="2.5" />
                <circle cx="20" cy="27" r="2.5" />
                <path d="M7.5 16h10M17.5 16V5M17.5 16v11M17.5 16h6" />
              </svg>

              Built on official data
            </h2>

            <span className="ml-auto rounded-full bg-[#ebebe5] px-[22px] py-3 text-sm text-[#1a1e24]">
              ONS + Nomis
            </span>

            <button
              ref={closeRef}
              type="button"
              onClick={closeModal}
              aria-label="Close sources"
              className="grid h-[46px] w-[46px] place-items-center rounded-full bg-[#ebebe5] text-[#1a1e24] transition-transform duration-300 hover:rotate-90"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                aria-hidden="true"
              >
                <path d="m2 2 10 10M12 2 2 12" />
              </svg>
            </button>
          </header>

          <p className="mb-7 mt-2 text-[15px] text-[#6b6f72]">
            Transparent sources. No guesswork.
          </p>

          <div className="grid grid-cols-1 gap-[34px] min-[561px]:grid-cols-2 min-[1001px]:grid-cols-4">
            {sources.map(
              (source, index) => (
                <article
                  key={source.code}
                  className={
                    open
                      ? "cs-rise"
                      : "opacity-0"
                  }
                  style={{
                    animationDelay: `${index * 70}ms`,
                  }}
                >
                  <p className="text-[11px] uppercase text-[#6b6f72]">
                    {source.category}
                  </p>

                  <a
                    href={source.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mb-2.5 mt-2 flex items-center justify-between gap-3 text-[24px] font-normal text-[#1a1e24] hover:underline"
                  >
                    {source.title}

                    <span aria-hidden="true">
                      ↗
                    </span>
                  </a>

                  <p className="mb-[22px] min-h-[40px] text-sm text-[#6b6f72]">
                    {
                      source.description
                    }
                  </p>

                  <code className="inline-block rounded-lg bg-[#ebebe5] px-3 py-2.5 text-[11px] text-[#1a1e24]">
                    {source.code}
                  </code>
                </article>
              ),
            )}
          </div>

          <footer className="mt-5 flex flex-wrap items-center justify-between gap-4 text-[13px] text-[#6b6f72]">
            <span>
              Different indicators use different reference periods.
            </span>

            <button
              type="button"
              onClick={closeModal}
              className="rounded-full bg-[#1a1e24] px-[22px] py-[13px] text-sm font-medium text-white transition hover:-translate-y-px hover:bg-[#2b3139] active:scale-[0.97]"
            >
              Done
            </button>
          </footer>
        </section>
      </div>
    </>
  );
}
