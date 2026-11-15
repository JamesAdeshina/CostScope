# CostScope UK --- Full Product & Engineering Brief

> **Project name:** CostScope UK\
> **Tagline:** Explore the cost of living across the UK.\
> **Project type:** Public, free-to-host data engineering + analytics
> platform\
> **Primary goal:** Build a production-style data product that ingests
> public UK datasets, transforms them into a consistent analytical
> model, exposes the data through an API, and provides an interactive
> web interface for location-level exploration.

------------------------------------------------------------------------

## 1. Executive Summary

CostScope UK is an interactive web platform for exploring how the cost
of living varies across UK locations.

A user should be able to search for a:

-   UK postcode
-   town/city
-   local authority
-   region

and receive a location profile containing selected indicators such as:

-   private rent
-   earnings
-   inflation / consumer prices
-   unemployment
-   energy-related costs
-   transport-related costs
-   historical trends
-   comparison with the UK average
-   comparison with other locations

The application is not simply a dashboard. The core portfolio value is
the **data platform underneath the interface**.

The intended architecture is:

``` text
Public UK datasets
        |
        v
Python ingestion
        |
        v
Raw / Bronze data
        |
        v
Validation + transformation
        |
        v
Silver / standardised data
        |
        v
Analytical Gold model
        |
        v
PostgreSQL / Supabase
        |
        v
FastAPI
        |
        v
Next.js web application
        |
        v
Public user
```

Automated refreshes are handled through GitHub Actions rather than
running a permanently hosted Airflow instance. This keeps the project
suitable for a £0/month portfolio deployment while still demonstrating
orchestration, automation, testing and CI/CD.

------------------------------------------------------------------------

# 2. Why Build This Project?

The project should demonstrate that the developer can:

1.  Find and work with real public datasets.
2.  Build ingestion pipelines.
3.  Handle APIs and CSV/Excel downloads.
4.  Standardise inconsistent schemas.
5.  Resolve geographic identifiers.
6.  Perform data-quality checks.
7.  Design a dimensional data model.
8.  Build analytical SQL.
9.  Automate recurring data refreshes.
10. Build a REST API.
11. Build a user-facing data application.
12. Deploy the complete system publicly.
13. Document assumptions, limitations and data provenance.

This makes CostScope UK substantially more useful as a Data Engineering
portfolio project than a standalone Power BI dashboard.

------------------------------------------------------------------------

# 3. Target Users

## Primary users

### General public

Someone wants to understand the cost of living in a particular UK area.

Example:

> "What does the cost of living look like in Derby compared with
> Nottingham?"

### Students / graduates

Someone deciding where to study, live or work.

### Job seekers

Someone comparing potential locations based on income and living costs.

### Researchers / analysts

Someone wanting a convenient interface for exploring public statistics.

### Recruiters / hiring managers

A technical audience evaluating the engineering quality of the platform.

------------------------------------------------------------------------

# 4. Core User Journey

The primary journey should be extremely simple:

``` text
Open CostScope UK
        |
        v
Search "DE1" / "Derby" / "Derbyshire"
        |
        v
Resolve location
        |
        v
Show location overview
        |
        +---- Housing
        |
        +---- Income & Employment
        |
        +---- Inflation & Prices
        |
        +---- Energy
        |
        +---- Transport
        |
        +---- Historical Trends
        |
        +---- Compare Locations
```

The user should not need to understand:

-   APIs
-   SQL
-   local authority codes
-   data sources
-   ETL
-   database tables

Those are implementation details.

------------------------------------------------------------------------

# 5. Product Name

## CostScope UK

### Tagline

> **Explore the cost of living across the UK.**

Alternative names considered:

-   LivingLens UK
-   CostMap UK
-   UK Living Index
-   CostAtlas
-   LifeCost UK
-   CostIQ

**CostScope UK** is the working product name.

------------------------------------------------------------------------

# 6. MVP Scope

The first public version should NOT attempt to include every possible
cost-of-living metric.

The MVP should focus on four core data domains:

### Domain 1 --- Housing

-   average / median private rent where available
-   rent growth
-   property size breakdown where available
-   historical rent trend

### Domain 2 --- Income

-   median earnings
-   earnings growth where available

### Domain 3 --- Prices

-   CPI / relevant inflation measure
-   inflation trend

### Domain 4 --- Employment

-   unemployment rate
-   employment-related indicator where geography and methodology support
    it

Then add:

### Domain 5 --- Location

-   postcode
-   local authority
-   region
-   country
-   geographic codes
-   latitude / longitude where appropriate

Energy and transport should be added after the core platform works.

------------------------------------------------------------------------

# 7. Important Data Principle

Do not invent local-level values where the source does not publish them.

For example, if a source provides regional energy prices but not
local-authority energy prices, the application should display the
regional figure and explicitly label it.

Example:

``` text
Energy cost

£1,420/year

Geography: East Midlands
Source: [source]
```

Do not imply:

``` text
Derby household energy cost = £1,420
```

unless the underlying dataset actually supports that level of geographic
attribution.

This is one of the most important analytical rules in the project.

------------------------------------------------------------------------

# 8. Data Sources

The initial data-source strategy should prioritise authoritative UK
public data.

## 8.1 Office for National Statistics

Use ONS for relevant:

-   earnings
-   inflation
-   employment
-   unemployment
-   population
-   housing statistics

The ONS developer hub provides programmatic access to datasets through
an API. The current beta API is open and does not require an API key,
although it is explicitly described as being in beta and potentially
subject to breaking changes.

Reference:

https://developer.ons.gov.uk/

API base:

https://api.beta.ons.gov.uk/v1

------------------------------------------------------------------------

## 8.2 ONS Private Rent and House Prices

The ONS publishes private rental statistics by local areas and wider
geographies.

This is particularly useful for CostScope UK because it provides a
direct housing-cost component.

Reference:

https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/privaterentandhousepricesuk/latest

The September 2026 release includes local-area private rent statistics
and notes that local rent estimates are available for local authorities
in England and Wales and Broad Rental Market Areas in Scotland and
Northern Ireland.

Do not assume that every UK geography has identical coverage or
frequency.

------------------------------------------------------------------------

## 8.3 Postcodes.io

Use Postcodes.io to resolve a user-entered UK postcode.

Example:

``` text
User:
DE1 1AA

        |

Postcodes.io

        |

Postcode:
DE1 1AA

Local authority:
Derby

Region:
East Midlands

Country:
England

Local authority code:
E06000015
```

Postcodes.io is a free UK postcode lookup/geocoder API and does not
require authentication.

Reference:

https://postcodes.io/docs/

Example endpoint:

``` text
GET https://api.postcodes.io/postcodes/{postcode}
```

Use this primarily for location resolution rather than storing every
postcode-level statistic in the CostScope database.

------------------------------------------------------------------------

# 9. Data Source Registry

Create a table in the database:

``` sql
CREATE TABLE data_sources (
    source_id SERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    publisher TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    geography_level TEXT,
    update_frequency TEXT,
    licence TEXT,
    last_checked_at TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);
```

Example records:

``` text
ONS | Office for National Statistics | Earnings
ONS | Office for National Statistics | Private rents
ONS | Office for National Statistics | CPI
ONS | Office for National Statistics | Employment
Postcodes.io | Ideal Postcodes | UK postcode lookup
```

This allows the application to expose data provenance.

------------------------------------------------------------------------

# 10. Architecture

## Free-hosted architecture

``` text
                           USER
                            |
                            v
                    +---------------+
                    |    Vercel     |
                    |    Next.js    |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    |    FastAPI    |
                    |      API      |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    |   Supabase    |
                    |  PostgreSQL   |
                    +-------+-------+
                            ^
                            |
                    +-------+-------+
                    | GitHub Actions|
                    | Scheduled ETL |
                    +-------+-------+
                            ^
                            |
                +-----------+-----------+
                |           |           |
               ONS       GOV.UK    Other public
               APIs       CSVs       datasets
```

------------------------------------------------------------------------

# 11. Hosting Strategy

The goal is to keep the project free for the MVP.

## Frontend

Recommended:

**Vercel**

Use it for:

-   Next.js
-   static assets
-   frontend deployment
-   automatic deployment from GitHub

Vercel's current Hobby plan is listed at \$0/month and supports personal
projects with automatic CI/CD.

Reference:

https://vercel.com/pricing

------------------------------------------------------------------------

## Database

Recommended:

**Supabase PostgreSQL**

Use it for:

-   analytical tables
-   location dimension
-   date dimension
-   metrics
-   data-quality logs
-   source metadata
-   API-facing queries

Supabase currently lists a 500 MB database-size quota for its Free plan,
so the project should avoid storing unnecessarily large raw datasets
inside PostgreSQL.

Reference:

https://supabase.com/docs/guides/platform/billing-on-supabase

------------------------------------------------------------------------

## API

Recommended:

**Render Free Web Service**

Use it for:

-   FastAPI
-   REST endpoints
-   health checks
-   database access

Render currently offers free web services, but free services spin down
after 15 minutes without inbound traffic and may take around a minute to
start again.

Reference:

https://render.com/docs/free

The application should therefore treat the API as a portfolio/demo
service, not a production SLA service.

------------------------------------------------------------------------

## ETL / Scheduling

Recommended:

**GitHub Actions**

Use it for:

-   scheduled ingestion
-   data validation
-   transformation
-   loading
-   tests
-   deployment checks

For public repositories, standard GitHub-hosted runners are currently
free and unlimited. GitHub also documents a standard free allowance for
GitHub Free accounts, so usage should still be kept sensible.

Reference:

https://docs.github.com/en/actions/reference/runners/github-hosted-runners

------------------------------------------------------------------------

# 12. Why Not AWS + Airflow + Redshift Initially?

Those technologies are valuable, but they are not required for the MVP.

The first version should prioritise:

``` text
Working data pipeline
        +
Good data model
        +
Reliable API
        +
Public web application
```

rather than infrastructure complexity.

Avoid building:

``` text
S3
+
Glue
+
Redshift
+
Airflow server
+
Lambda
+
ECS
+
CloudWatch
```

just to make the architecture look impressive.

If the project later needs a cloud-engineering version, AWS can be
introduced as **V2**.

------------------------------------------------------------------------

# 13. Technology Stack

## Frontend

``` text
Next.js
TypeScript
Tailwind CSS
Recharts
```

Optional:

``` text
Leaflet / MapLibre
```

for maps.

------------------------------------------------------------------------

## Backend

``` text
Python
FastAPI
Pydantic
SQLAlchemy
psycopg
```

------------------------------------------------------------------------

## Data engineering

``` text
Python
Pandas or Polars
DuckDB
PyArrow
```

Use PySpark only if the dataset size or transformation complexity
actually justifies it.

------------------------------------------------------------------------

## Database

``` text
PostgreSQL
Supabase
```

------------------------------------------------------------------------

## Automation

``` text
GitHub Actions
```

------------------------------------------------------------------------

## Testing

``` text
pytest
```

Potentially:

``` text
Great Expectations
```

or a lightweight custom validation framework.

------------------------------------------------------------------------

# 14. Repository Structure

Recommended monorepo:

``` text
costscope-uk/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── styles/
│   ├── package.json
│   └── tsconfig.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── repositories/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── data_pipeline/
│   ├── config/
│   ├── extract/
│   ├── transform/
│   ├── load/
│   ├── quality/
│   ├── utils/
│   └── main.py
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── sample/
│
├── sql/
│   ├── schema/
│   ├── views/
│   ├── functions/
│   └── seeds/
│
├── tests/
│   ├── data_quality/
│   └── integration/
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── methodology.md
│   ├── data_sources.md
│   └── api.md
│
└── .github/
    └── workflows/
        ├── test.yml
        ├── pipeline.yml
        └── deploy.yml
```

------------------------------------------------------------------------

# 15. Data Pipeline

The pipeline should follow:

``` text
EXTRACT
   |
   v
RAW / BRONZE
   |
   v
VALIDATE
   |
   v
TRANSFORM
   |
   v
SILVER
   |
   v
MODEL
   |
   v
GOLD
   |
   v
POSTGRES
```

------------------------------------------------------------------------

# 16. Extraction Layer

Create individual connectors.

Example:

``` text
data_pipeline/extract/
    ons_earnings.py
    ons_rent.py
    ons_inflation.py
    ons_employment.py
    postcode_lookup.py
```

Each extractor should return a predictable structure.

Example:

``` python
def extract_dataset() -> pd.DataFrame: ...
```

Do not mix extraction, transformation and database loading in one
enormous script.

------------------------------------------------------------------------

# 17. Extraction Metadata

Every ingestion should record:

``` text
source
dataset
run_id
started_at
completed_at
status
records_received
source_last_updated
error_message
```

Example:

``` json
{
  "run_id": "2026-09-27T02:00:00Z",
  "dataset": "private_rent",
  "status": "success",
  "records_received": 12842
}
```

------------------------------------------------------------------------

# 18. Bronze Layer

Bronze should preserve source information.

Example:

``` text
data/bronze/ons/rent/
    2026-09-01.csv
    2026-10-01.csv
```

or:

``` text
data/bronze/ons/rent/
    ingestion_date=2026-09-27/
        data.parquet
```

Never silently overwrite the only copy of raw data during development.

------------------------------------------------------------------------

# 19. Silver Layer

The Silver layer standardises:

-   column names
-   data types
-   dates
-   geographic codes
-   units
-   missing values
-   duplicate records

Example:

Raw:

``` text
Area name
Date
Average private rent
```

Silver:

``` text
location_name
location_code
observation_date
rent_monthly_gbp
source
```

------------------------------------------------------------------------

# 20. Gold Layer

Gold is designed for application queries.

Example:

``` text
fact_cost_metrics
```

contains:

``` text
date_key
location_key
metric_key
value
unit
source_id
```

This allows the application to query multiple indicators consistently.

------------------------------------------------------------------------

# 21. Database Model

Use a star-schema-inspired analytical model.

## DimLocation

``` sql
CREATE TABLE dim_location (
    location_key SERIAL PRIMARY KEY,
    location_code TEXT UNIQUE NOT NULL,
    location_name TEXT NOT NULL,
    location_type TEXT NOT NULL,
    local_authority_code TEXT,
    local_authority_name TEXT,
    region_code TEXT,
    region_name TEXT,
    country TEXT,
    latitude NUMERIC,
    longitude NUMERIC
);
```

------------------------------------------------------------------------

## DimDate

``` sql
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL
);
```

------------------------------------------------------------------------

## DimMetric

``` sql
CREATE TABLE dim_metric (
    metric_key SERIAL PRIMARY KEY,
    metric_code TEXT UNIQUE NOT NULL,
    metric_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    description TEXT,
    source_id INTEGER
);
```

Example metrics:

``` text
RENT_MONTHLY
EARNINGS_ANNUAL
CPI_ANNUAL_RATE
UNEMPLOYMENT_RATE
ENERGY_COST
TRANSPORT_COST
```

------------------------------------------------------------------------

## FactCostMetric

``` sql
CREATE TABLE fact_cost_metric (
    fact_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    location_key INTEGER NOT NULL,
    metric_key INTEGER NOT NULL,
    value NUMERIC NOT NULL,
    source_id INTEGER,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Add appropriate foreign keys and indexes.

------------------------------------------------------------------------

# 22. Data Quality

Data quality is a major portfolio feature.

Every dataset should have checks for:

## Completeness

``` text
Required columns exist
Required values are not unexpectedly null
```

## Uniqueness

``` text
No duplicate location/date/metric records
```

## Validity

Examples:

``` text
Rent > 0
Earnings > 0
Inflation between sensible bounds
Unemployment >= 0
```

Do not use arbitrary hard-coded limits without documenting why they
exist.

------------------------------------------------------------------------

## Referential integrity

Every:

``` text
location_key
metric_key
date_key
```

must resolve to a dimension record.

------------------------------------------------------------------------

## Freshness

Record:

``` text
source_updated_at
ingested_at
```

Then calculate:

``` text
freshness_days =
ingested_at - source_updated_at
```

------------------------------------------------------------------------

# 23. Data Quality Log

Create:

``` sql
CREATE TABLE data_quality_log (
    quality_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    dataset TEXT NOT NULL,
    check_name TEXT NOT NULL,
    status TEXT NOT NULL,
    failed_records INTEGER DEFAULT 0,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT
);
```

Example:

``` text
private_rent | schema_check       | PASS
private_rent | duplicate_check    | PASS
private_rent | null_check         | PASS
private_rent | range_check        | PASS
```

------------------------------------------------------------------------

# 24. CostScope Index

The project can optionally provide a composite CostScope Index.

This must be presented as a **project-defined analytical measure**, not
an official UK statistic.

## Principle

A transparent index can combine:

-   housing
-   income
-   energy
-   transport
-   prices

Each component should be normalised before combining.

Example:

``` text
UK baseline = 100

Housing       32%
Energy        18%
Transport     15%
Prices        15%
Income        20%
```

However, the exact weights should be treated as a methodology decision
and documented.

Do not present the index as:

> "The official cost of living score."

Instead:

> "CostScope Index --- a project-defined composite measure."

------------------------------------------------------------------------

# 25. Normalisation

A simple approach is:

``` text
normalised_value =
    local_value / UK_baseline * 100
```

For metrics where a higher value means lower cost, such as income, the
direction must be handled appropriately.

The methodology should explicitly document:

1.  Baseline.
2.  Component metrics.
3.  Weights.
4.  Directionality.
5.  Missing-data treatment.
6.  Geographic aggregation.
7.  Rounding.
8.  Update frequency.

------------------------------------------------------------------------

# 26. Missing Data

Do not automatically impute every missing value.

There are several different cases:

### Missing because source does not publish the metric

Show:

``` text
Not available at this geography
```

### Missing because the source has a temporary gap

Flag the observation.

### Missing because ingestion failed

Do not replace it with a fabricated value.

The UI should distinguish:

``` text
Not available
Delayed
Unavailable
No data
```

from an actual zero.

------------------------------------------------------------------------

# 27. API Design

FastAPI should provide a clean read API.

## Health

``` http
GET /health
```

Response:

``` json
{
  "status": "ok"
}
```

------------------------------------------------------------------------

## Search

``` http
GET /api/v1/search?q=derby
```

Response:

``` json
{
  "results": [
    {
      "name": "Derby",
      "type": "local_authority",
      "code": "E06000015"
    }
  ]
}
```

------------------------------------------------------------------------

## Postcode resolution

``` http
GET /api/v1/postcode/DE11AA
```

Response:

``` json
{
  "postcode": "DE1 1AA",
  "local_authority": "Derby",
  "local_authority_code": "E06000015",
  "region": "East Midlands",
  "country": "England"
}
```

------------------------------------------------------------------------

## Location overview

``` http
GET /api/v1/locations/E06000015/overview
```

Response:

``` json
{
  "location": "Derby",
  "metrics": {
    "rent": 895,
    "earnings": 31200,
    "inflation": 3.2,
    "unemployment": 4.8
  }
}
```

------------------------------------------------------------------------

## Historical data

``` http
GET /api/v1/locations/E06000015/history?metric=rent
```

------------------------------------------------------------------------

## Comparison

``` http
GET /api/v1/compare?locations=E06000015,E06000021,E06000016
```

------------------------------------------------------------------------

## Sources

``` http
GET /api/v1/locations/E06000015/sources
```

------------------------------------------------------------------------

# 28. API Principles

The API should:

-   use versioning
-   return predictable JSON
-   validate parameters
-   return meaningful HTTP status codes
-   avoid exposing database implementation details
-   use pagination for large results
-   provide source metadata
-   avoid returning unnecessary fields

API version:

``` text
/api/v1/
```

------------------------------------------------------------------------

# 29. Frontend

## Main navigation

``` text
Overview
Housing
Income & Employment
Energy
Transport
Inflation & Prices
Compare Locations
Historical Trends
Data & Methodology
About
```

------------------------------------------------------------------------

# 30. Homepage

The homepage should be focused.

``` text
CostScope UK

Explore the cost of living across the UK.

[ Search postcode, town or local authority... ]

Popular locations

[London] [Manchester] [Birmingham] [Derby] [Leeds]
```

Include a short explanation:

> CostScope UK brings together selected public UK statistics to help
> users explore differences in housing, income, prices and other
> cost-related indicators.

------------------------------------------------------------------------

# 31. Location Overview

Example:

``` text
DERBY
East Midlands
Local Authority: Derby

-------------------------------------------------

Median / Average Rent
£895 / month

Median Earnings
£31,200 / year

Inflation
3.2%

Unemployment
4.8%

-------------------------------------------------

CostScope Index
97.4
UK = 100

-------------------------------------------------

Rent trend
[chart]

Income trend
[chart]

-------------------------------------------------

Compare Derby with:

[Nottingham]
[Leicester]
[Sheffield]
```

------------------------------------------------------------------------

# 32. Metric Cards

Every metric card should show:

``` text
Metric
Value
Unit
Change
Reference period
Geography
Source
```

Example:

``` text
Median rent

£895 / month

+4.1% YoY

August 2026

Source: ONS
```

Do not show fake precision.

If the source is rounded to the nearest pound, don't display:

``` text
£895.2371
```

------------------------------------------------------------------------

# 33. Charts

Recommended charts:

### Rent

Line chart:

``` text
2019 → 2026
```

### Income

Line chart:

``` text
2019 → latest
```

### Comparison

Horizontal bar chart.

### Cost components

Donut or segmented bar.

### Geography

Map / choropleth if boundary data is available and the implementation
remains manageable.

------------------------------------------------------------------------

# 34. Comparison Page

Allow users to select 2--5 locations.

Example:

``` text
Compare locations

[ Derby       ]
[ Nottingham  ]
[ Leicester   ]
[ Sheffield   ]

------------------------------------------------

Metric              Derby   Nottingham   Leicester

Rent                £895    £920         £870
Earnings            £31.2k  £32.8k       £30.4k
Inflation           3.2%    3.3%         3.1%
Unemployment        4.8%    5.1%         5.3%
```

Avoid language such as:

``` text
BEST CITY
WORST CITY
WINNER
```

The platform should present the underlying measurements and methodology
rather than making life decisions for the user.

------------------------------------------------------------------------

# 35. Data & Methodology Page

This page is essential.

Include:

## What is CostScope UK?

Short description.

## Data sources

For every source:

``` text
Publisher
Dataset
Geography
Frequency
Last updated
Licence
Source link
```

## CostScope Index methodology

Explain the calculation.

## Limitations

Explain:

-   different data frequencies
-   different geographic levels
-   provisional statistics
-   revisions
-   missing data
-   estimates
-   comparability limitations

------------------------------------------------------------------------

# 36. Data Freshness

Every page should show the relevant period.

Example:

``` text
Updated:
Rent — August 2026
Earnings — 2025
Inflation — August 2026
Unemployment — latest available period
```

Do not present all metrics as if they represent the same month.

This is an important analytical distinction.

------------------------------------------------------------------------

# 37. GitHub Actions

Create:

``` text
.github/workflows/pipeline.yml
```

Conceptually:

``` yaml
name: Data Pipeline

on:
  schedule:
    - cron: "0 2 * * 1"

  workflow_dispatch:

jobs:
  pipeline:
    runs-on: ubuntu-latest

    steps:
      - checkout repository

      - setup Python

      - install dependencies

      - run extraction

      - run validation

      - run transformations

      - run tests

      - load database

      - publish pipeline status
```

The schedule should ultimately be aligned with the actual update
frequencies of the source datasets.

Do not run a monthly dataset ingestion every hour simply because it is
possible.

------------------------------------------------------------------------

# 38. Pipeline Run States

Use:

``` text
STARTED
EXTRACTING
VALIDATING
TRANSFORMING
LOADING
SUCCESS
FAILED
```

A run should have a unique ID.

Example:

``` text
run_20260927_020000
```

------------------------------------------------------------------------

# 39. Environment Variables

Never commit secrets.

`.env.example`:

``` text
DATABASE_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
POSTCODES_API_URL=https://api.postcodes.io
```

The actual secrets belong in:

-   local `.env`
-   GitHub Actions Secrets
-   Render Environment Variables
-   Vercel Environment Variables

------------------------------------------------------------------------

# 40. Security

Minimum requirements:

-   no database password in Git
-   no service-role key in frontend
-   validate API parameters
-   use parameterised SQL
-   configure CORS
-   use HTTPS
-   restrict database permissions
-   expose only required endpoints

The browser should never receive the Supabase service-role key.

------------------------------------------------------------------------

# 41. Database Security

The frontend should communicate with:

``` text
Frontend
    |
    v
FastAPI
    |
    v
Database
```

not:

``` text
Frontend
    |
    v
Database with privileged credentials
```

unless there is a deliberate reason to use Supabase's client-side
security model.

For this project, keeping the analytical database behind FastAPI makes
the architecture easy to explain.

------------------------------------------------------------------------

# 42. Testing

## Unit tests

Test:

-   extraction functions
-   postcode parsing
-   transformation functions
-   normalisation
-   index calculation

Example:

``` python
def test_cost_index(): ...
```

------------------------------------------------------------------------

## Data tests

Check:

``` text
Required columns
Null percentages
Duplicate records
Date ranges
Valid geography codes
Positive monetary values
```

------------------------------------------------------------------------

## API tests

Test:

``` text
GET /health
GET /search
GET /locations/{id}
GET /locations/{id}/history
GET /compare
```

------------------------------------------------------------------------

# 43. CI Pipeline

Every pull request should ideally run:

``` text
Lint
  |
Type check
  |
Unit tests
  |
Data-quality tests
  |
Build frontend
  |
Build backend
```

Only merge if the required checks pass.

------------------------------------------------------------------------

# 44. Local Development

Recommended:

``` bash
git clone <repository>
cd costscope-uk
```

Backend:

``` bash
cd backend
python -m venv .venv
```

Windows:

``` bash
.venv\Scripts\activate
```

Install:

``` bash
pip install -r requirements.txt
```

Run:

``` bash
uvicorn app.main:app --reload
```

Frontend:

``` bash
cd frontend
npm install
npm run dev
```

------------------------------------------------------------------------

# 45. Local Database

Use Supabase for the deployed environment.

For local development, either:

### Option A --- Local PostgreSQL

Use Docker:

``` bash
docker compose up -d postgres
```

### Option B --- Development Supabase project

Use a dedicated development project.

Do not use production tables while experimenting with migrations.

------------------------------------------------------------------------

# 46. Development Phases

## Phase 0 --- Repository

Create:

``` text
GitHub repository
README
.gitignore
environment configuration
folder structure
```

------------------------------------------------------------------------

## Phase 1 --- First Dataset

Start with **private rent**.

Do not start with five datasets simultaneously.

Deliver:

``` text
Download data
        |
Clean data
        |
Standardise geography
        |
Store in PostgreSQL
        |
Query Derby
```

Success condition:

``` text
GET /locations/derby/rent
```

returns real source-backed data.

------------------------------------------------------------------------

# 47. Phase 2 --- Add Earnings

Add:

``` text
Earnings
```

Create:

``` text
metric = EARNINGS_ANNUAL
```

Update:

``` text
fact_cost_metric
```

Success condition:

``` text
Derby overview

Rent
Earnings
```

works.

------------------------------------------------------------------------

# 48. Phase 3 --- Add Inflation

Add CPI / relevant inflation measure.

Success condition:

``` text
Rent
Earnings
Inflation
```

appear on the location page.

------------------------------------------------------------------------

# 49. Phase 4 --- Add Employment

Add unemployment/employment indicator where geography and methodology
are appropriate.

Now the initial CostScope profile exists.

------------------------------------------------------------------------

# 50. Phase 5 --- Build API

Implement:

``` text
/health
/search
/postcode/{postcode}
/locations/{id}
/locations/{id}/history
/compare
/sources
```

Add tests.

------------------------------------------------------------------------

# 51. Phase 6 --- Build Frontend

Start with:

``` text
Homepage
Location page
Comparison page
Methodology page
```

Do not build every navigation item before the core flow works.

------------------------------------------------------------------------

# 52. Phase 7 --- Automate

Move the pipeline into GitHub Actions.

Create:

``` text
pipeline.yml
```

Run:

``` text
extract
validate
transform
load
```

on a sensible schedule.

------------------------------------------------------------------------

# 53. Phase 8 --- Deploy

Deploy:

``` text
Frontend → Vercel
API → Render
Database → Supabase
Pipeline → GitHub Actions
```

Then test the public application from a clean browser.

------------------------------------------------------------------------

# 54. Phase 9 --- Add Energy and Transport

Only after the first four domains work.

Before adding a new domain, ask:

1.  Is the source authoritative?
2.  Is the geography compatible?
3.  Is the update frequency known?
4.  Is the methodology documented?
5.  Can it be legally redistributed?
6.  Does it improve the product?

------------------------------------------------------------------------

# 55. Phase 10 --- Data Platform Monitoring

Create an internal or public read-only page:

``` text
Data Platform Health

Dataset              Status       Latest data

Private rent         PASS         Aug 2026
Earnings             PASS         2025
Inflation             PASS         Aug 2026
Employment            PASS         Latest

Pipeline status
Last successful run
Records processed
Records rejected
Quality checks passed
```

This is particularly useful for demonstrating Data Engineering skills.

------------------------------------------------------------------------

# 56. Deployment Architecture

Final MVP:

``` text
                      INTERNET
                          |
                          v
                +-------------------+
                |      VERCEL       |
                |      NEXT.JS      |
                +---------+---------+
                          |
                          | HTTPS
                          v
                +-------------------+
                |      RENDER       |
                |      FASTAPI      |
                +---------+---------+
                          |
                          | SQL
                          v
                +-------------------+
                |     SUPABASE      |
                |    POSTGRESQL     |
                +---------^---------+
                          |
                          |
                +---------+---------+
                |  GITHUB ACTIONS   |
                |   DATA PIPELINE   |
                +---------^---------+
                          |
             +------------+------------+
             |            |            |
            ONS         GOV.UK    Other sources
```

------------------------------------------------------------------------

# 57. Free Hosting Constraints

The platform should be designed around free-tier limitations.

## Supabase

The Free plan currently has a 500 MB database-size quota.

Therefore:

-   do not store unnecessary raw data
-   use efficient numeric types
-   index only useful columns
-   archive large raw files elsewhere
-   store analytical/serving data in Postgres

------------------------------------------------------------------------

## Render

Free web services can spin down after inactivity.

Therefore:

-   expect cold starts
-   implement `/health`
-   keep API startup lightweight
-   avoid loading large datasets into memory at startup

Do not load an entire DataFrame every time FastAPI starts.

------------------------------------------------------------------------

## Vercel

Keep frontend/serverless workloads lightweight.

Use the API for data-heavy processing rather than trying to process
large datasets in the browser.

------------------------------------------------------------------------

## GitHub Actions

Keep workflows efficient.

Do not download and process the entire historical dataset every day if
only the latest monthly release changed.

------------------------------------------------------------------------

# 58. Performance Strategy

The API should query pre-modelled tables.

Avoid:

``` text
API request
    |
    v
Download ONS dataset
    |
    v
Pandas transformation
    |
    v
Return result
```

Instead:

``` text
Scheduled pipeline
    |
    v
Transform data
    |
    v
PostgreSQL
    |
    v
FastAPI
    |
    v
User
```

This is the correct separation between **data processing** and **data
serving**.

------------------------------------------------------------------------

# 59. Caching

Add caching only after measuring a need.

Potentially cache:

``` text
popular locations
location overview
comparison results
```

Do not prematurely add Redis just because it appears in modern
architectures.

------------------------------------------------------------------------

# 60. Observability

At minimum capture:

``` text
API request logs
pipeline logs
pipeline status
data-quality status
database errors
```

FastAPI should expose:

``` text
/health
```

Potentially:

``` text
/health/database
```

for deeper diagnostics.

------------------------------------------------------------------------

# 61. Error Handling

If ONS fails:

``` text
Pipeline:
FAILED

Dataset:
ONS earnings

Reason:
HTTP/API failure

Action:
No database update performed
```

Do not overwrite a good previous dataset with an empty or broken
response.

------------------------------------------------------------------------

# 62. Data Versioning

Keep:

``` text
source_last_updated
ingestion_timestamp
pipeline_run_id
```

This lets you explain exactly when a record entered the platform.

Example:

``` text
Source updated:
16 Sep 2026

Ingested:
17 Sep 2026 02:04

Pipeline:
run_20260917_020000
```

------------------------------------------------------------------------

# 63. Methodology Rules

Every metric must answer:

``` text
What?
Where?
When?
How?
Source?
```

Example:

``` text
Metric:
Private rent

Definition:
Average monthly private rent

Geography:
Local authority

Period:
August 2026

Source:
ONS

Status:
Provisional / final as applicable
```

------------------------------------------------------------------------

# 64. Do Not Mix Geographies Carelessly

A major analytical risk is comparing:

``` text
Derby local authority
```

with:

``` text
East Midlands region
```

as if they are equivalent.

The database must store:

``` text
location_type
```

such as:

``` text
postcode
local_authority
region
country
```

The UI should make the geography visible.

------------------------------------------------------------------------

# 65. Do Not Mix Time Periods Silently

Example:

``` text
Rent: August 2026
Inflation: August 2026
Earnings: 2025
Unemployment: latest available period
```

The UI should show those periods.

A single dashboard timestamp such as:

``` text
Updated September 2026
```

is not sufficient.

------------------------------------------------------------------------

# 66. UX Principles

The application should feel like a data product, not a spreadsheet.

Use:

-   strong hierarchy
-   concise metric cards
-   clean charts
-   clear source labels
-   obvious comparison controls
-   consistent units
-   meaningful empty states
-   responsive design

Avoid:

-   excessive charts
-   giant tables
-   unexplained indexes
-   fake precision
-   decorative animations that slow the experience

------------------------------------------------------------------------

# 67. Visual Direction

Recommended:

``` text
Style:
Modern analytical SaaS

Background:
Light neutral

Primary:
Deep navy / blue

Cards:
White

Borders:
Subtle

Typography:
Inter / Geist / system sans

Charts:
Minimal gridlines

Icons:
Lucide
```

Dark mode can be added later.

------------------------------------------------------------------------

# 68. Location Page Information Architecture

``` text
Location Header
|
+-- Location identity
|     Derby
|     East Midlands
|     Local Authority
|
+-- KPI cards
|     Rent
|     Earnings
|     Inflation
|     Unemployment
|
+-- CostScope Index
|
+-- Historical trend
|
+-- Housing
|
+-- Income
|
+-- Prices
|
+-- Employment
|
+-- Comparison
|
+-- Data source / freshness
```

------------------------------------------------------------------------

# 69. Search Behaviour

The search bar should support:

``` text
DE1
DE1 1AA
Derby
Derbyshire
Nottingham
Manchester
```

The application should resolve ambiguous results.

Example:

``` text
Search:
Derby

Results:

Derby
Local Authority
East Midlands

Derbyshire
County
East Midlands
```

Do not silently assume which geography the user intended.

------------------------------------------------------------------------

# 70. Accessibility

Minimum:

-   keyboard navigation
-   visible focus states
-   semantic HTML
-   sufficient contrast
-   accessible chart descriptions
-   form labels
-   meaningful error messages
-   responsive layout
-   screen-reader-friendly controls

Do not communicate important information using colour alone.

------------------------------------------------------------------------

# 71. SEO

The location pages should eventually have indexable metadata.

Example:

``` text
/cost-of-living/derby
/cost-of-living/nottingham
/cost-of-living/leeds
```

Page title:

``` text
Cost of Living in Derby | CostScope UK
```

Meta description:

``` text
Explore housing, earnings, inflation and other public cost-of-living indicators for Derby.
```

------------------------------------------------------------------------

# 72. Analytics

Do not add invasive tracking initially.

If analytics are needed, prefer privacy-conscious analytics.

Track only useful product events such as:

``` text
location_search
comparison_created
metric_viewed
```

Do not collect unnecessary personal data.

------------------------------------------------------------------------

# 73. README Structure

The public GitHub README should contain:

``` text
CostScope UK

Short description

Live Demo
GitHub
Architecture

Features

Tech Stack

Data Sources

Data Pipeline

Database Schema

API

Local Development

Deployment

Data Quality

Methodology

Limitations

Screenshots

Future Work
```

------------------------------------------------------------------------

# 74. Portfolio Description

Use a concise portfolio description:

> **CostScope UK --- End-to-End Data Platform**
>
> Built a public UK cost-of-living data platform integrating government
> datasets for housing, earnings, inflation and employment. Developed
> automated Python ETL pipelines, data-quality validation, dimensional
> PostgreSQL models and FastAPI endpoints powering an interactive
> Next.js application.

------------------------------------------------------------------------

# 75. CV Bullet Options

### Data Engineering version

> Built an end-to-end UK cost-of-living data platform integrating public
> government datasets through automated Python ETL pipelines,
> standardising geographic and temporal dimensions, and loading
> analytical PostgreSQL models for API consumption.

### Cloud / deployment version

> Deployed a full-stack data product using Next.js, FastAPI,
> PostgreSQL/Supabase, Vercel, Render and GitHub Actions, with scheduled
> data ingestion and automated validation.

### Data quality version

> Implemented automated schema, completeness, duplicate, range and
> referential-integrity checks to prevent invalid source updates from
> reaching analytical tables.

### API version

> Developed versioned FastAPI endpoints for postcode resolution,
> location profiles, historical trends and multi-location comparisons.

------------------------------------------------------------------------

# 76. Interview Talking Points

If asked:

## "Why did you build this?"

Answer:

> I wanted a project where the user-facing application depended on a
> genuine data engineering pipeline rather than simply visualising a
> static dataset. CostScope UK gave me an opportunity to work with
> multiple public sources, deal with different geographic and temporal
> granularities, automate ingestion and expose the resulting analytical
> model through an API.

------------------------------------------------------------------------

## "Why GitHub Actions instead of Airflow?"

Answer:

> For the MVP, the datasets do not justify running a dedicated
> orchestration environment. GitHub Actions provides scheduled workflows
> and CI/CD at no infrastructure cost for a public repository. If the
> platform grew to require complex DAG dependencies, retries, backfills
> and operational scheduling across many pipelines, I would consider
> Airflow or a managed orchestration service.

------------------------------------------------------------------------

## "Why PostgreSQL?"

Answer:

> The application primarily needs relational analytical queries over
> well-defined dimensions such as location, date and metric. PostgreSQL
> is sufficient for the initial scale, widely supported and easy to
> deploy. I would reassess the warehouse technology if data volume or
> analytical workload increased substantially.

------------------------------------------------------------------------

## "Why not process data on every API request?"

Answer:

> Data transformation belongs in the pipeline rather than the serving
> layer. Pre-processing the data allows the API to return predictable
> results quickly and separates ingestion from consumption.

------------------------------------------------------------------------

# 77. Definition of Done --- MVP

The MVP is finished when all of these are true:

### Data

-   [ ] At least 3 authoritative datasets integrated
-   [ ] Data sources documented
-   [ ] Geography mapping implemented
-   [ ] Dates standardised
-   [ ] Data quality checks implemented
-   [ ] Source timestamps stored

### Engineering

-   [ ] Extraction modules separated
-   [ ] Transformation modules separated
-   [ ] Database loading implemented
-   [ ] Scheduled GitHub Action exists
-   [ ] Pipeline failures are visible
-   [ ] Tests exist

### Database

-   [ ] DimLocation
-   [ ] DimDate
-   [ ] DimMetric
-   [ ] FactCostMetric
-   [ ] DataSources
-   [ ] DataQualityLog

### API

-   [ ] Health endpoint
-   [ ] Search endpoint
-   [ ] Postcode endpoint
-   [ ] Location overview
-   [ ] Historical trends
-   [ ] Comparison endpoint
-   [ ] Source metadata

### Frontend

-   [ ] Homepage
-   [ ] Search
-   [ ] Location overview
-   [ ] Charts
-   [ ] Comparison
-   [ ] Methodology
-   [ ] Data freshness

### Deployment

-   [ ] GitHub repository
-   [ ] Vercel frontend
-   [ ] Render API
-   [ ] Supabase database
-   [ ] Automated pipeline
-   [ ] Public live URL
-   [ ] Production environment variables configured

------------------------------------------------------------------------

# 78. V2 Features

Only after the MVP works:

## Additional datasets

-   Energy
-   Transport
-   House prices
-   Household expenditure
-   Population
-   Council tax
-   Fuel prices
-   Broadband
-   Childcare
-   Food prices where suitable public data exists

## Product features

-   saved comparisons
-   shareable location URLs
-   downloadable CSV
-   downloadable reports
-   interactive UK map
-   regional ranking views
-   custom metric selection
-   API documentation
-   public API key system

## Engineering features

-   Airflow version
-   AWS S3 data lake
-   Spark processing
-   dbt
-   Terraform
-   Docker
-   CI/CD environments
-   observability
-   automated backfills

------------------------------------------------------------------------

# 79. V3 --- Cloud Data Engineering Version

If the project needs to demonstrate more advanced cloud engineering:

``` text
Government APIs
      |
      v
AWS EventBridge / Scheduler
      |
      v
AWS Lambda / ECS
      |
      v
S3 Bronze
      |
      v
Glue / Spark
      |
      v
S3 Silver
      |
      v
dbt
      |
      v
Redshift
      |
      v
FastAPI
      |
      v
Next.js
```

This should be treated as an evolution, not a requirement for the first
release.

------------------------------------------------------------------------

# 80. Project Timeline

## Day 1

Repository + architecture:

``` text
GitHub
Next.js
FastAPI
Supabase
environment configuration
```

## Day 2

First dataset:

``` text
ONS rent
```

Extract → transform → database.

## Day 3

Second dataset:

``` text
Earnings
```

Add dimensional model.

## Day 4

Third dataset:

``` text
Inflation
```

Add data-quality tests.

## Day 5

FastAPI:

``` text
search
postcode
location
history
```

## Day 6

Frontend:

``` text
homepage
search
location page
```

## Day 7

Charts + comparison.

## Day 8

GitHub Actions + automated refresh.

## Day 9

Deployment:

``` text
Vercel
Render
Supabase
```

## Day 10

Polish:

``` text
methodology
sources
README
tests
error states
responsive UI
```

This is an aggressive MVP schedule. It is realistic only if the first
release deliberately limits the number of datasets and features.

------------------------------------------------------------------------

# 81. Immediate Build Order

Start here.

### Step 1

Create repository:

``` text
costscope-uk
```

### Step 2

Create:

``` text
frontend/
backend/
data_pipeline/
sql/
tests/
docs/
.github/workflows/
```

### Step 3

Create Supabase project.

### Step 4

Create:

``` text
dim_location
dim_date
dim_metric
fact_cost_metric
data_sources
data_quality_log
```

### Step 5

Build ONS rent extractor.

### Step 6

Load rent data.

### Step 7

Build:

``` text
GET /api/v1/locations/{id}/overview
```

### Step 8

Build the first Derby location page.

### Step 9

Add earnings.

### Step 10

Add inflation.

### Step 11

Add comparison.

### Step 12

Automate the pipeline.

### Step 13

Deploy.

### Step 14

Add energy/transport only after the core system is live.

------------------------------------------------------------------------

# 82. First Technical Milestone

The first milestone should be extremely concrete:

> **A user enters a postcode and sees a real, source-backed housing
> metric for the corresponding local authority in a public web
> application.**

For example:

``` text
User
 |
 | DE1 1AA
 v
Postcodes.io
 |
 | Derby / E06000015
 v
FastAPI
 |
 v
PostgreSQL
 |
 | ONS private rent
 v
Frontend

Derby
Private rent:
£X / month

Source:
ONS

Period:
YYYY-MM
```

Once this works, the project is no longer theoretical.

Everything else becomes incremental.

------------------------------------------------------------------------

# 83. Engineering Rules

1.  **Source data is never silently overwritten.**
2.  **Every metric has a source and reference period.**
3.  **Do not confuse missing with zero.**
4.  **Do not mix geographic levels without explaining it.**
5.  **Do not mix time periods without showing them.**
6.  **Do not fabricate local estimates.**
7.  **Do not put secrets in Git.**
8.  **Do not process large datasets during every API request.**
9.  **Do not use Spark unless the data/problem justifies it.**
10. **Do not build infrastructure purely for résumé keywords.**
11. **Automate repeatable processes.**
12. **Test transformations before loading production tables.**
13. **Keep the methodology transparent.**
14. **Make the application useful before making it complex.**

------------------------------------------------------------------------

# 84. Final Architecture Decision

For the initial public version, use:

``` text
                COSTSCOPE UK
                     |
          +----------+----------+
          |                     |
       FRONTEND               API
       Next.js              FastAPI
          |                     |
          +----------+----------+
                     |
                PostgreSQL
                 Supabase
                     ^
                     |
              GitHub Actions
                     ^
                     |
               Python ETL
                     ^
                     |
          Public UK datasets
```

### Final stack

``` text
Frontend       Next.js + TypeScript + Tailwind
Charts         Recharts
Backend        FastAPI + Python
Database       PostgreSQL / Supabase
ETL            Python + Pandas/Polars + DuckDB
Validation     pytest + data-quality checks
Scheduling     GitHub Actions
Deployment     Vercel + Render + Supabase
Location       Postcodes.io
Versioning     Git/GitHub
```

### Target cost

``` text
Development:       £0
Hosting MVP:       £0
Database MVP:      £0
API MVP:           £0
Frontend MVP:      £0
ETL scheduling:    £0
Domain:            Optional paid upgrade
```

Free-tier limits and provider policies can change, so verify current
quotas before deployment.

------------------------------------------------------------------------

# 85. Success Criteria

CostScope UK should eventually allow a stranger to open the website and
answer:

> **"What does the cost of living look like in this UK location?"**

within a few seconds.

Behind that simple experience, the project should demonstrate:

``` text
Public Data
     ↓
Ingestion
     ↓
Validation
     ↓
Transformation
     ↓
Data Modelling
     ↓
Automation
     ↓
PostgreSQL
     ↓
API
     ↓
Web Application
     ↓
Real User
```

That complete chain is the project.

**The dashboard is the visible layer.\
The data platform is the portfolio piece.**
