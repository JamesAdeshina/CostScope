"""
Authoritative public-data source definitions used by CostScope.

Source metadata is centralised so ingestion code does not scatter URLs,
dataset identifiers or series identifiers throughout the codebase.
"""

# =====================================================================
# ONS Annual Survey of Hours and Earnings (ASHE)
# =====================================================================

ONS_ASHE_TABLE8_2025_URL = (
    "https://www.ons.gov.uk/file?"
    "uri=%2Femploymentandlabourmarket%2Fpeopleinwork%2F"
    "earningsandworkinghours%2Fdatasets%2F"
    "placeofresidencebylocalauthorityashetable8%2F"
    "2025provisional%2Fashetable82025provisional.zip"
)

ONS_ASHE_DATASET_NAME = (
    "Earnings and hours worked, place of residence by local authority: ASHE Table 8"
)

ONS_ASHE_RELEASE = "2025 provisional"

ONS_ASHE_RELEASE_YEAR = 2025

ONS_ASHE_PUBLISHER = "Office for National Statistics"

ONS_ASHE_TARGET_TABLE = "8.7a"

ONS_ASHE_TARGET_MEASURE = "annual pay"

ONS_ASHE_TARGET_PAY_TYPE = "gross"

ONS_ASHE_TARGET_SHEET = "Full-Time"


# =====================================================================
# ONS Consumer Price Inflation
# =====================================================================

ONS_CPI_DATASET_ID = "MM23"

ONS_CPI_DATASET_NAME = "Consumer price inflation time series"

ONS_CPI_PUBLISHER = "Office for National Statistics"

ONS_CPI_RELEASE_DATE = "2026-09-16"

ONS_API_BASE_URL = "https://api.beta.ons.gov.uk/v1"

# Headline CPI annual inflation rate.
ONS_CPI_ANNUAL_SERIES_ID = "D7G7"

# Month-on-month CPI rate.
ONS_CPI_MONTHLY_SERIES_ID = "D7OE"

# CPI all-items index, 2015 = 100.
ONS_CPI_INDEX_SERIES_ID = "D7BT"

ONS_CPI_SERIES = {
    "annual_rate": {
        "series_id": ONS_CPI_ANNUAL_SERIES_ID,
        "metric_code": "CPI_ANNUAL_RATE",
        "description": ("CPI annual rate 00: all items 2015=100"),
        "unit": "percent",
    },
    "monthly_rate": {
        "series_id": ONS_CPI_MONTHLY_SERIES_ID,
        "metric_code": "CPI_MONTHLY_RATE",
        "description": ("CPI monthly rate 00: all items 2015=100"),
        "unit": "percent",
    },
    "index": {
        "series_id": ONS_CPI_INDEX_SERIES_ID,
        "metric_code": "CPI_INDEX",
        "description": ("CPI index 00: all items 2015=100"),
        "unit": "index",
    },
}
