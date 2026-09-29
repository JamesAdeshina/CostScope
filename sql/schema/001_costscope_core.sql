-- ============================================================
-- CostScope Core Analytical Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS data_sources (
    source_id SMALLINT PRIMARY KEY,
    source_code VARCHAR(50) NOT NULL UNIQUE,
    publisher VARCHAR(200) NOT NULL,
    dataset_name VARCHAR(300) NOT NULL,
    source_url TEXT,
    geography_description TEXT,
    update_frequency VARCHAR(100),
    licence VARCHAR(200),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS dim_location (
    location_key BIGINT PRIMARY KEY,
    location_id TEXT NOT NULL UNIQUE,
    official_area_code VARCHAR(30),
    location_name VARCHAR(250) NOT NULL,
    region_or_country_name VARCHAR(250),
    has_official_code BOOLEAN NOT NULL
);


CREATE INDEX IF NOT EXISTS idx_dim_location_area_code
    ON dim_location (official_area_code);


CREATE INDEX IF NOT EXISTS idx_dim_location_name
    ON dim_location (location_name);


CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL
);


CREATE TABLE IF NOT EXISTS dim_metric (
    metric_key SMALLINT PRIMARY KEY,
    metric_code VARCHAR(100) NOT NULL UNIQUE,
    metric_name VARCHAR(250) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    description TEXT
);


CREATE TABLE IF NOT EXISTS fact_cost_metric (
    fact_id BIGINT PRIMARY KEY,

    date_key INTEGER NOT NULL
        REFERENCES dim_date(date_key),

    location_key BIGINT NOT NULL
        REFERENCES dim_location(location_key),

    metric_key SMALLINT NOT NULL
        REFERENCES dim_metric(metric_key),

    source_id SMALLINT NOT NULL
        REFERENCES data_sources(source_id),

    value DOUBLE PRECISION,

    is_published BOOLEAN NOT NULL DEFAULT TRUE,

    loaded_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT uq_fact_cost_metric
        UNIQUE (
            date_key,
            location_key,
            metric_key,
            source_id
        )
);


CREATE INDEX IF NOT EXISTS idx_fact_location
    ON fact_cost_metric (location_key);


CREATE INDEX IF NOT EXISTS idx_fact_metric
    ON fact_cost_metric (metric_key);


CREATE INDEX IF NOT EXISTS idx_fact_date
    ON fact_cost_metric (date_key);


INSERT INTO data_sources (
    source_id,
    source_code,
    publisher,
    dataset_name,
    geography_description,
    update_frequency,
    licence,
    active
)
VALUES (
    1,
    'ONS_PIPR',
    'Office for National Statistics',
    'Price Index of Private Rents, UK: monthly price statistics',
    'ONS published UK rental geographies',
    'Monthly',
    'Open Government Licence',
    TRUE
)
ON CONFLICT (source_id) DO NOTHING;