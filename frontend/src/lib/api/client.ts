import type {
  LocationOverviewResponse,
  LocationSearchResult,
  MetricHistoryResponse,
  PostcodeOverviewResponse,
} from "@/types/api";

const API_BASE = "/backend-api/api/v1";

async function request<T>(
  path: string,
): Promise<T> {
  const response = await fetch(
    `${API_BASE}${path}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const body = await response.json();

      if (
        body &&
        typeof body === "object" &&
        "detail" in body
      ) {
        message = String(body.detail);
      }
    } catch {
      // Keep generic message if response is not JSON.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function searchLocations(
  query: string,
): Promise<LocationSearchResult[]> {
  return request<LocationSearchResult[]>(
    `/search?q=${encodeURIComponent(query)}`,
  );
}

export function getLocationOverview(
  locationCode: string,
): Promise<LocationOverviewResponse> {
  return request<LocationOverviewResponse>(
    `/locations/${encodeURIComponent(locationCode)}/overview`,
  );
}

export function getPostcodeOverview(
  postcode: string,
): Promise<PostcodeOverviewResponse> {
  return request<PostcodeOverviewResponse>(
    `/postcode/${encodeURIComponent(postcode)}`,
  );
}

export function getRentHistory(
  locationCode: string,
): Promise<MetricHistoryResponse> {
  return request<MetricHistoryResponse>(
    `/locations/${encodeURIComponent(locationCode)}/history?metric=rent`,
  );
}
