"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";


interface CountUpProps {
  value: number | null | undefined;
  format: (value: number) => string;
  duration?: number;
  fallback?: string;
}


/**
 * Animates a number from 0 to `value` (ease-out cubic, 1.1s by default),
 * matching the count-up in costscope.html. Re-runs whenever `value` changes
 * and respects prefers-reduced-motion.
 */
export function CountUp({
  value,
  format,
  duration = 1100,
  fallback = "—",
}: CountUpProps) {
  const [display, setDisplay] =
    useState(0);

  const frame =
    useRef<number | null>(null);

  useEffect(() => {
    if (
      typeof value !== "number" ||
      !Number.isFinite(value)
    ) {
      return;
    }

    const target = value;

    if (
      window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches
    ) {
      setDisplay(target);

      return;
    }

    const start =
      performance.now();

    function step(now: number) {
      const progress = Math.min(
        (now - start) / duration,
        1,
      );

      const eased =
        1 - Math.pow(1 - progress, 3);

      setDisplay(target * eased);

      if (progress < 1) {
        frame.current =
          requestAnimationFrame(step);
      }
    }

    frame.current =
      requestAnimationFrame(step);

    return () => {
      if (frame.current !== null) {
        cancelAnimationFrame(
          frame.current,
        );
      }
    };
  }, [value, duration]);

  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return <>{fallback}</>;
  }

  return <>{format(display)}</>;
}
