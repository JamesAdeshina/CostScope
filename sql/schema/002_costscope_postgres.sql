-- ============================================================================
-- CostScope PostgreSQL analytical warehouse
-- ============================================================================
--
-- Grain:
--   fact_cost_metric
--     one metric
--     for one location
--     for one reference date
--     from one source
--
-- Gold Parquet remains the pipeline output.
-- PostgreSQL becomes the serving warehouse for the API.
-- ============================================================================


CREATE SCHEMA IF NOT EXISTS costscope;


-- ============================================================================
-- SOURCE DIMENSION
-- ============================================================================

CREATE TABLE IF NOT EXISTS costscope.dim_source (
    source_id       SMALLINT PRIMARY KEY,
    source_code     VARCHAR(64) NOT NULL UNIQUE,
    publisher       VARCHAR(255) NOT NULL,
    dataset_name    TEXT NOT NULL,
    source_system   VARCHAR(64) NOT NULL,
    geography_note  TEXT,
    source_url      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- LOCATION DIMENSION
-- ============================================================================

CREATE TABLE IF NOT EXISTS costscope.dim_location (
    location_key            BIGINT PRIMARY KEY,
    location_id             VARCHAR(255) NOT NULL UNIQUE,
    official_area_code      VARCHAR(32),
    location_name           VARCHAR(255) NOT NULL,
    region_or_country_name  VARCHAR(255),
    has_official_code       BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT ck_location_official_code
        CHECK (
            has_official_code = FALSE
            OR official_area_code IS NOT NULL
        )
);


CREATE INDEX IF NOT EXISTS ix_dim_location_name
    ON costscope.dim_location (location_name);


CREATE INDEX IF NOT EXISTS ix_dim_location_official_area_code
    ON costscope.dim_location (official_area_code);


CREATE INDEX IF NOT EXISTS ix_dim_location_region
    ON costscope.dim_location (region_or_country_name);


-- ============================================================================
-- DATE DIMENSION
-- ============================================================================

CREATE TABLE IF NOT EXISTS costscope.dim_date (
    date_key     INTEGER PRIMARY KEY,
    date         DATE NOT NULL UNIQUE,
    year         SMALLINT NOT NULL,
    quarter      SMALLINT NOT NULL,
    month        SMALLINT NOT NULL,
    month_name   VARCHAR(16) NOT NULL,

    CONSTRAINT ck_date_quarter
        CHECK (quarter BETWEEN 1 AND 4),

    CONSTRAINT ck_date_month
        CHECK (month BETWEEN 1 AND 12)
);


CREATE INDEX IF NOT EXISTS ix_dim_date_year_month
    ON costscope.dim_date (year, month);


-- ============================================================================
-- METRIC DIMENSION
-- ============================================================================

CREATE TABLE IF NOT EXISTS costscope.dim_metric (
    metric_key   INTEGER PRIMARY KEY,
    metric_code  VARCHAR(128) NOT NULL UNIQUE,
    metric_name  VARCHAR(255) NOT NULL,
    unit         VARCHAR(64) NOT NULL,
    category     VARCHAR(64)
);


CREATE INDEX IF NOT EXISTS ix_dim_metric_category
    ON costscope.dim_metric (category);


-- ============================================================================
-- CENTRAL FACT TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS costscope.fact_cost_metric (
    fact_id        BIGINT PRIMARY KEY,
    date_key       INTEGER NOT NULL,
    location_key   BIGINT NOT NULL,
    metric_key     INTEGER NOT NULL,
    value          DOUBLE PRECISION,
    is_published   BOOLEAN NOT NULL DEFAULT TRUE,
    source_id      SMALLINT NOT NULL,
    loaded_at      TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES costscope.dim_date (date_key),

    CONSTRAINT fk_fact_location
        FOREIGN KEY (location_key)
        REFERENCES costscope.dim_location (location_key),

    CONSTRAINT fk_fact_metric
        FOREIGN KEY (metric_key)
        REFERENCES costscope.dim_metric (metric_key),

    CONSTRAINT fk_fact_source
        FOREIGN KEY (source_id)
        REFERENCES costscope.dim_source (source_id),

    CONSTRAINT uq_fact_metric_grain
        UNIQUE (
            date_key,
            location_key,
            metric_key,
            source_id
        )
);


CREATE INDEX IF NOT EXISTS ix_fact_location_metric_date
    ON costscope.fact_cost_metric (
        location_key,
        metric_key,
        date_key DESC
    );


CREATE INDEX IF NOT EXISTS ix_fact_metric_date
    ON costscope.fact_cost_metric (
        metric_key,
        date_key DESC
    );


CREATE INDEX IF NOT EXISTS ix_fact_source
    ON costscope.fact_cost_metric (
        source_id
    );


CREATE INDEX IF NOT EXISTS ix_fact_published
    ON costscope.fact_cost_metric (
        is_published
    );


-- ============================================================================
-- SERVING VIEW
-- ============================================================================
--
-- Useful for API queries and manual inspection.
-- ============================================================================

CREATE OR REPLACE VIEW costscope.vw_cost_metrics AS
SELECT
    f.fact_id,

    d.date_key,
    d.date AS reference_period,
    d.year,
    d.quarter,
    d.month,

    l.location_key,
    l.location_id,
    l.official_area_code,
    l.location_name,
    l.region_or_country_name,

    m.metric_key,
    m.metric_code,
    m.metric_name,
    m.unit,
    m.category,

    f.value,
    f.is_published,

    s.source_id,
    s.source_code,
    s.publisher,
    s.dataset_name,

    f.loaded_at

FROM costscope.fact_cost_metric AS f

INNER JOIN costscope.dim_date AS d
    ON d.date_key = f.date_key

INNER JOIN costscope.dim_location AS l
    ON l.location_key = f.location_key

INNER JOIN costscope.dim_metric AS m
    ON m.metric_key = f.metric_key

INNER JOIN costscope.dim_source AS s
    ON s.source_id = f.source_id;
