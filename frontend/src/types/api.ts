export interface LocationSummary {
  location_id: string;
  location_code: string;
  name: string;
  region_or_country: string | null;
}

export interface RentOverview {
  monthly_rent: number;
  unit: string;
  reference_period: string;
  monthly_change_percent: number | null;
  annual_change_percent: number | null;
}

export interface EarningsOverview {
  median_annual_pay: number;
  unit: string;
  reference_period: string;
  annual_change_percent: number | null;
}

export interface InflationOverview {
  annual_rate_percent: number;
  monthly_rate_percent: number | null;
  index_value: number | null;
  index_base: string;
  reference_period: string;
  geography_name: string;
  geography_code: string;
}

export interface UnemploymentOverview {
  rate_percent: number;
  unit: string;
  reference_period: string;
  geography_name: string;
  geography_code: string;
  methodology: string;
}

export interface SourceMetadata {
  source_code: string;
  publisher: string;
  dataset: string;
}

export interface LocationOverviewResponse {
  location: LocationSummary;
  rent: RentOverview | null;
  earnings: EarningsOverview | null;
  inflation: InflationOverview | null;
  unemployment: UnemploymentOverview | null;
  sources: SourceMetadata[];
}

export interface PostcodeSummary {
  postcode: string;
  admin_district: string;
  admin_district_code: string;
  region: string;
  country: string;
  latitude: number;
  longitude: number;
}

export interface PostcodeOverviewResponse {
  postcode: PostcodeSummary;
  overview: LocationOverviewResponse;
}

export interface LocationSearchResult {
  location_id: string;
  location_code: string;
  name: string;
  region_or_country: string | null;
}

export interface MetricHistoryObservation {
  reference_period: string;
  value: number;
}

export interface MetricHistoryResponse {
  location: LocationSummary;
  metric_code: string;
  metric_name: string;
  unit: string;
  observations: MetricHistoryObservation[];
  source: SourceMetadata;
}
