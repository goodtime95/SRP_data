"""
Projet SRP (Structured Retail Products) - Collecte et analyse de données
"""

from .models import (
    SRPProduct, 
    SRPProductList, 
    SRPAnalysis,
    Country, 
    Currency, 
    ProductType, 
    RiskLevel
)
from .data_collector import SRPDataCollector
from .analyzer import SRPAnalyzer
from .utils import (
    generate_sample_srp_data,
    create_sample_json_file,
    validate_srp_data,
    print_srp_summary,
    convert_to_srp_products
)

__version__ = "1.0.0"
__author__ = "Victor Bontemps"
__description__ = "Collecte et analyse des produits SRP en France et en Belgique"

__all__ = [
    # Modèles
    "SRPProduct",
    "SRPProductList", 
    "SRPAnalysis",
    "Country",
    "Currency",
    "ProductType",
    "RiskLevel",
    
    # Classes principales
    "SRPDataCollector",
    "SRPAnalyzer",
    
    # Utilitaires
    "generate_sample_srp_data",
    "create_sample_json_file", 
    "validate_srp_data",
    "print_srp_summary",
    "convert_to_srp_products"
]

def hello():
    """Fonction de test simple"""
    return f"Hello from {__description__} v{__version__}!"

if __name__ == "__main__":
    print(hello())
    print("\nComposants disponibles:")
    for component in __all__:
        print(f"  - {component}")
