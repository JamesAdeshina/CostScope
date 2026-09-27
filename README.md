# CostScope

> Explore the cost of living across the UK.

CostScope is an end-to-end data engineering and analytics platform that
integrates authoritative UK public datasets covering housing, earnings,
inflation, employment and other cost-of-living indicators.

The project is designed to demonstrate the complete journey from public
source data to a production-style user-facing analytical application.

---

## Architecture

```text
Public UK Data
      |
      v
Python Extraction
      |
      v
Bronze / Raw
      |
      v
Validation
      |
      v
Silver / Standardised
      |
      v
Gold / Analytical Model
      |
      v
PostgreSQL
      |
      v
FastAPI
      |
      v
Next.js
      |
      v
User