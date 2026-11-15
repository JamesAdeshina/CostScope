"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";


interface UkMapProps {
  latitude?: number | null;
  longitude?: number | null;
  region?: string | null;
  locationName?: string;
  className?: string;
  /** Colour of the thin lines between regions. Use the card colour. */
  outlineColor?: string;
  /** Enables hover feedback on map regions. */
  interactive?: boolean;
}


const MAP = {
  west: -10.476361,
  north: 60.846142,
  east: 1.765083,
  south: 49.1626,
  width: 628.09174,
  height: 1051.4788,
};


/* Full source SVG viewBox so the UK is never cropped inside cards. */
const VIEW_BOX = "0 0 628.09174 1051.4788";


const REGION_IDS: Record<
  string,
  string
> = {
  "North East": "GB-UKC",
  "North West": "GB-UKD",
  "Yorkshire and The Humber":
    "GB-UKE",
  "Yorkshire and the Humber":
    "GB-UKE",
  "East Midlands": "GB-UKF",
  "West Midlands": "GB-UKG",
  "East of England": "GB-UKH",
  London: "GB-UKI",
  "South East": "GB-UKJ",
  "South West": "GB-UKK",
  Wales: "GB-UKL",
  Scotland: "GB-UKM",
  "Northern Ireland": "GB-UKN",
};


const UK_REGION_IDS =
  new Set(
    Object.values(REGION_IDS),
  );


function mercatorLatitude(
  latitude: number,
): number {
  return Math.log(
    Math.tan(
      Math.PI / 4 +
        (latitude * Math.PI) /
          360,
    ),
  );
}


export function projectToUkMap(
  longitude: number,
  latitude: number,
) {
  const longitudeRange =
    MAP.east - MAP.west;

  const x =
    ((longitude - MAP.west) /
      longitudeRange) *
    MAP.width;

  const northMercator =
    mercatorLatitude(
      MAP.north,
    );

  const southMercator =
    mercatorLatitude(
      MAP.south,
    );

  const latitudeMercator =
    mercatorLatitude(
      latitude,
    );

  const y =
    ((northMercator -
      latitudeMercator) /
      (northMercator -
        southMercator)) *
    MAP.height;

  return {
    x,
    y,
  };
}


/*
 * Builds the static markup once per SVG file. Selection styling is applied
 * afterwards in an effect so the existing <path> elements stay in the DOM
 * and the opacity change can transition (as in costscope.html).
 */
function prepareMapMarkup(
  svgText: string,
): string {
  const parser =
    new DOMParser();

  const document =
    parser.parseFromString(
      svgText,
      "image/svg+xml",
    );

  const root =
    document.documentElement;

  root
    .querySelectorAll("path")
    .forEach((path) => {
      const id =
        path.getAttribute("id");

      const isUkRegion =
        id !== null &&
        UK_REGION_IDS.has(id);

      path.setAttribute(
        "fill",
        "#1a1e24",
      );

      path.style.fillOpacity =
        isUkRegion
          ? "0.16"
          : "0.07";

      path.style.transition =
        "fill-opacity 600ms ease";
    });

  return root.innerHTML;
}


export function UkMap({
  latitude,
  longitude,
  region,
  locationName,
  className = "",
  outlineColor = "#e8ef7a",
  interactive = false,
}: UkMapProps) {
  const [
    svgText,
    setSvgText,
  ] = useState<string | null>(
    null,
  );

  const groupRef =
    useRef<SVGGElement>(null);

  const selectedRegionId =
    region
      ? REGION_IDS[region] ??
        null
      : null;

  useEffect(() => {
    let active = true;

    async function loadMap() {
      const response =
        await fetch(
          "/maps/united-kingdom.svg",
        );

      if (!response.ok) {
        return;
      }

      const text =
        await response.text();

      if (active) {
        setSvgText(text);
      }
    }

    void loadMap();

    return () => {
      active = false;
    };
  }, []);


  const mapMarkup =
    useMemo(() => {
      if (!svgText) {
        return "";
      }

      return prepareMapMarkup(
        svgText,
      );
    }, [svgText]);


  useEffect(() => {
    const group =
      groupRef.current;

    if (!group) {
      return;
    }

    group
      .querySelectorAll("path")
      .forEach((path) => {
        const id =
          path.getAttribute("id");

        const isUkRegion =
          id !== null &&
          UK_REGION_IDS.has(id);

        const isSelected =
          selectedRegionId !==
            null &&
          id === selectedRegionId;

        path.style.fillOpacity =
          isSelected
            ? "1"
            : isUkRegion
              ? "0.16"
              : "0.07";

        path.style.stroke =
          outlineColor;

        path.style.strokeWidth =
          "1.2";

        path.style.strokeLinejoin =
          "round";
      });
  }, [
    mapMarkup,
    selectedRegionId,
    outlineColor,
  ]);


  const hasCoordinates =
    latitude !== null &&
    latitude !== undefined &&
    longitude !== null &&
    longitude !== undefined;

  const point =
    hasCoordinates
      ? projectToUkMap(
          longitude,
          latitude,
        )
      : null;


  function restorePathOpacity(
    path: SVGPathElement,
  ) {
    const id = path.getAttribute("id");

    const isUkRegion =
      id !== null &&
      UK_REGION_IDS.has(id);

    const isSelected =
      selectedRegionId !== null &&
      id === selectedRegionId;

    path.style.fillOpacity =
      isSelected
        ? "1"
        : isUkRegion
          ? "0.16"
          : "0.07";
  }


  return (
    <svg
      viewBox={VIEW_BOX}
      role="img"
      aria-label={
        locationName
          ? `Map showing ${locationName}`
          : "Map of the United Kingdom"
      }
      className={className}
      preserveAspectRatio="xMidYMid meet"
      onPointerOver={(event) => {
        if (
          !interactive ||
          !(event.target instanceof SVGPathElement)
        ) {
          return;
        }

        const path = event.target;
        const id = path.getAttribute("id");

        if (
          id &&
          UK_REGION_IDS.has(id) &&
          id !== selectedRegionId
        ) {
          path.style.fillOpacity = "0.48";
          path.style.cursor = "pointer";
        }
      }}
      onPointerOut={(event) => {
        if (
          !interactive ||
          !(event.target instanceof SVGPathElement)
        ) {
          return;
        }

        restorePathOpacity(
          event.target,
        );
      }}
    >
      {mapMarkup && (
        <g
          ref={groupRef}
          dangerouslySetInnerHTML={{
            __html: mapMarkup,
          }}
        />
      )}

      {point && (
        <g
          aria-label={
            locationName ??
            "Selected location"
          }
        >
          <circle
            className="cs-pulse"
            cx={point.x}
            cy={point.y}
            r="9"
          />

          <circle
            cx={point.x}
            cy={point.y}
            r="8"
            fill="#e8ef7a"
            stroke="#1a1e24"
            strokeWidth="3"
          />
        </g>
      )}
    </svg>
  );
}
