"""
Configuration du projet SRP (Structured Retail Products)
"""
import os
from datetime import datetime, date
from typing import List, Dict, Any

# Configuration des dates
START_DATE = date(2024, 8, 15)  # 15 août 2024
END_DATE = date.today()

# Configuration des pays
COUNTRIES = ["FR", "BE"]  # France et Belgique

# Configuration des API (à adapter selon la source de données)
API_CONFIG = {
    "base_url": os.getenv("SRP_API_BASE_URL", "https://api.example.com"),
    "api_key": os.getenv("SRP_API_KEY", ""),
    "timeout": 30,
    "max_retries": 3
}

# Configuration des champs clés à extraire
KEY_FIELDS = [
    "product_id",
    "product_name",
    "issuer",
    "country",
    "currency",
    "issue_date",
    "maturity_date",
    "nominal_value",
    "coupon_rate",
    "product_type",
    "underlying_asset",
    "risk_level",
    "rating"
]

# Configuration des filtres d'analyse
ANALYSIS_FILTERS = {
    "min_nominal_value": 1000,  # Valeur nominale minimale en EUR
    "max_risk_level": 5,  # Niveau de risque maximum (1-5)
    "currencies": ["EUR", "USD", "GBP"]
}

# Configuration des exports
EXPORT_CONFIG = {
    "output_dir": "output",
    "json_filename": "srp_products.json",
    "analysis_filename": "srp_analysis.json",
    "report_filename": "srp_report.html"
}
