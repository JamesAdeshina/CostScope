import Image from "next/image";
import Link from "next/link";


interface CostScopeLogoProps {
  compact?: boolean;
}


export function CostScopeLogo({
  compact = false,
}: CostScopeLogoProps) {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-2.5"
      aria-label="CostScope home"
    >
      <Image
        src={
          compact
            ? "/brand/costscope-icon.svg"
            : "/brand/costscope-icon.svg"
        }
        alt=""
        width={32}
        height={32}
        priority
        className="h-8 w-8"
      />

      {!compact && (
        <span className="flex items-start">
          <span className="text-[28px] font-medium tracking-[-0.04em] text-[#1a1e24]">
            CostScope
          </span>

          <sup className="ml-1 mt-1 text-[10px] font-medium text-[#6b6f72]">
            UK
          </sup>
        </span>
      )}
    </Link>
  );
}
