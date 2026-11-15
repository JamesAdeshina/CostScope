"use client";

import Image from "next/image";
import Link from "next/link";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";


type NavKey =
  | "explore"
  | "about"
  | "data";


interface SiteHeaderProps {
  active?: NavKey;
}


interface PillState {
  left: number;
  width: number;
}


const STORAGE_KEY =
  "costscope:nav-pill";


const navItems = [
  {
    key: "explore",
    label: "Explore",
    href: "/",
  },
  {
    key: "about",
    label: "About",
    href: "/about",
  },
  {
    key: "data",
    label: "Data",
    href: "/data",
  },
] as const;


export function SiteHeader({
  active = "explore",
}: SiteHeaderProps) {
  const links = useRef<
    Partial<
      Record<
        NavKey,
        HTMLAnchorElement | null
      >
    >
  >({});

  const [
    pill,
    setPill,
  ] = useState<PillState | null>(
    null,
  );

  const [
    animate,
    setAnimate,
  ] = useState(false);


  const measure =
    useCallback((): PillState | null => {
      const element =
        links.current[active];

      if (!element) {
        return null;
      }

      return {
        left:
          element.offsetLeft,
        width:
          element.offsetWidth,
      };
    }, [active]);


  /*
   * Keep the sliding navigation pill
   * animated between Next.js routes.
   */
  useEffect(() => {
    const target =
      measure();

    if (!target) {
      return;
    }

    let previous:
      | PillState
      | null = null;

    try {
      const raw =
        window.sessionStorage.getItem(
          STORAGE_KEY,
        );

      if (raw) {
        previous =
          JSON.parse(
            raw,
          ) as PillState;
      }
    } catch {
      previous = null;
    }

    let frame = 0;

    if (
      previous &&
      (
        previous.left !==
          target.left ||
        previous.width !==
          target.width
      )
    ) {
      setAnimate(false);
      setPill(previous);

      frame =
        requestAnimationFrame(
          () => {
            frame =
              requestAnimationFrame(
                () => {
                  setAnimate(
                    true,
                  );

                  setPill(
                    target,
                  );
                },
              );
          },
        );
    } else {
      setPill(target);
    }

    try {
      window.sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(
          target,
        ),
      );
    } catch {
      /*
       * Session storage may be
       * unavailable in some browsers.
       */
    }

    return () => {
      cancelAnimationFrame(
        frame,
      );
    };
  }, [measure]);


  /*
   * Recalculate pill position if
   * viewport or font metrics change.
   */
  useEffect(() => {
    function remeasure() {
      const target =
        measure();

      if (!target) {
        return;
      }

      setAnimate(false);
      setPill(target);
    }

    window.addEventListener(
      "resize",
      remeasure,
    );

    void document.fonts?.ready.then(
      remeasure,
    );

    return () => {
      window.removeEventListener(
        "resize",
        remeasure,
      );
    };
  }, [measure]);


  return (
    <header className="grid grid-cols-[1fr_auto] items-center gap-6 pb-[34px] pt-[22px] min-[1001px]:grid-cols-[1fr_auto_1fr] min-[1001px]:pt-[34px]">

      {/* ================================================
          COSTSCOPE BRAND
          Uses:
          public/brand/costscope-logo.svg
          ================================================ */}

      <Link
        href="/"
        aria-label="CostScope UK home"
        className="flex w-fit items-center"
      >
        <Image
          src="/brand/costscope-logo.svg"
          alt="CostScope UK"
          width={190}
          height={42}
          priority
          className="h-auto w-[150px] object-contain min-[561px]:w-[175px] min-[1001px]:w-[190px]"
        />
      </Link>


      {/* ================================================
          PRIMARY NAVIGATION
          ================================================ */}

      <nav
        className="relative flex rounded-full bg-[#ebebe5] p-1"
        aria-label="Primary navigation"
      >
        <span
          aria-hidden="true"
          className="absolute bottom-1 top-1 rounded-full bg-[#1a1e24]"
          style={{
            left:
              pill?.left ?? 0,
            width:
              pill?.width ?? 0,
            opacity:
              pill ? 1 : 0,
            transition:
              animate
                ? "left .35s cubic-bezier(.4,0,.2,1), width .35s cubic-bezier(.4,0,.2,1)"
                : "none",
          }}
        />

        {navItems.map(
          (item) => {
            const selected =
              active ===
              item.key;

            return (
              <Link
                key={
                  item.key
                }
                href={
                  item.href
                }
                ref={(
                  element,
                ) => {
                  links.current[
                    item.key
                  ] =
                    element;
                }}
                aria-current={
                  selected
                    ? "page"
                    : undefined
                }
                className={[
                  "relative z-10 rounded-full px-[25px] py-[11px] text-[15px] font-medium transition-colors duration-300",
                  selected
                    ? pill
                      ? "text-white"
                      : "bg-[#1a1e24] text-white"
                    : "text-[#1a1e24]",
                ].join(" ")}
              >
                {
                  item.label
                }
              </Link>
            );
          },
        )}
      </nav>


      {/* ================================================
          TAGLINE
          ================================================ */}

      <p className="hidden justify-self-end text-sm text-[#6b6f72] min-[1001px]:block">
        Official data. Everyday clarity.
      </p>
    </header>
  );
}