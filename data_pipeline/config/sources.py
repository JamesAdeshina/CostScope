"""
Authoritative public-data source definitions used by CostScope.

Keeping source metadata in one module makes dataset provenance explicit
and avoids scattering source URLs throughout extraction code.
"""

# ---------------------------------------------------------------------
# ONS Annual Survey of Hours and Earnings (ASHE)
#
# Dataset:
# Earnings and hours worked, place of residence by local authority
# ASHE Table 8
#
# Edition:
# 2025 provisional
#
# CostScope target:
# Table 8.7a - Annual pay - Gross
# ---------------------------------------------------------------------

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

# We deliberately match by semantic tokens rather than one exact
# filename because ONS filenames may contain variable whitespace.
ONS_ASHE_TARGET_TABLE = "8.7a"

ONS_ASHE_TARGET_MEASURE = "annual pay"

ONS_ASHE_TARGET_PAY_TYPE = "gross"

ONS_ASHE_TARGET_SHEET = "Full-Time"
