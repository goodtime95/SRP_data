"""
Modèles de données pour les produits SRP (Structured Retail Products)
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class RiskLevel(str, Enum):
    """Niveaux de risque des produits SRP"""
    VERY_LOW = "1"
    LOW = "2"
    MEDIUM = "3"
    HIGH = "4"
    VERY_HIGH = "5"

class ProductType(str, Enum):
    """Types de produits SRP"""
    BOND = "bond"
    NOTE = "note"
    CERTIFICATE = "certificate"
    WARRANT = "warrant"
    OPTION = "option"
    FUTURE = "future"
    SWAP = "swap"
    OTHER = "other"

class Currency(str, Enum):
    """Devises supportées"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"
    JPY = "JPY"

class Country(str, Enum):
    """Pays supportés"""
    FRANCE = "FR"
    BELGIUM = "BE"

class SRPProduct(BaseModel):
    """Modèle principal pour un produit SRP"""
    product_id: str = Field(..., description="Identifiant unique du produit")
    product_name: str = Field(..., description="Nom du produit")
    issuer: str = Field(..., description="Émetteur du produit")
    country: Country = Field(..., description="Pays d'émission")
    currency: Currency = Field(..., description="Devise du produit")
    issue_date: date = Field(..., description="Date d'émission")
    maturity_date: Optional[date] = Field(None, description="Date d'échéance")
    nominal_value: float = Field(..., description="Valeur nominale")
    coupon_rate: Optional[float] = Field(None, description="Taux de coupon (%)")
    product_type: ProductType = Field(..., description="Type de produit")
    underlying_asset: Optional[str] = Field(None, description="Actif sous-jacent")
    risk_level: RiskLevel = Field(..., description="Niveau de risque")
    rating: Optional[str] = Field(None, description="Rating du produit")
    
    # Champs additionnels
    isin: Optional[str] = Field(None, description="Code ISIN")
    cusip: Optional[str] = Field(None, description="Code CUSIP")
    min_investment: Optional[float] = Field(None, description="Investissement minimum")
    max_investment: Optional[float] = Field(None, description="Investissement maximum")
    liquidity: Optional[str] = Field(None, description="Niveau de liquidité")
    fees: Optional[float] = Field(None, description="Frais (%)")
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('nominal_value')
    def validate_nominal_value(cls, v):
        if v <= 0:
            raise ValueError('La valeur nominale doit être positive')
        return v
    
    @validator('coupon_rate')
    def validate_coupon_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Le taux de coupon doit être entre 0 et 100%')
        return v
    
    @validator('maturity_date')
    def validate_maturity_date(cls, v, values):
        if v and 'issue_date' in values and v <= values['issue_date']:
            raise ValueError('La date d\'échéance doit être postérieure à la date d\'émission')
        return v

class SRPProductList(BaseModel):
    """Liste de produits SRP avec métadonnées"""
    products: List[SRPProduct] = Field(default_factory=list)
    total_count: int = Field(0, description="Nombre total de produits")
    countries: List[Country] = Field(default_factory=list)
    currencies: List[Currency] = Field(default_factory=list)
    date_range: Dict[str, date] = Field(default_factory=dict)
    
    def add_product(self, product: SRPProduct):
        """Ajoute un produit à la liste"""
        self.products.append(product)
        self.total_count = len(self.products)
        
        if product.country not in self.countries:
            self.countries.append(product.country)
        
        if product.currency not in self.currencies:
            self.currencies.append(product.currency)
    
    def get_products_by_country(self, country: Country) -> List[SRPProduct]:
        """Récupère les produits par pays"""
        return [p for p in self.products if p.country == country]
    
    def get_products_by_currency(self, currency: Currency) -> List[SRPProduct]:
        """Récupère les produits par devise"""
        return [p for p in self.products if p.currency == currency]
    
    def get_products_by_risk_level(self, risk_level: RiskLevel) -> List[SRPProduct]:
        """Récupère les produits par niveau de risque"""
        return [p for p in self.products if p.risk_level == risk_level]

class SRPAnalysis(BaseModel):
    """Résultats de l'analyse des produits SRP"""
    total_products: int = Field(0, description="Nombre total de produits")
    total_value: float = Field(0, description="Valeur totale des produits")
    average_nominal_value: float = Field(0, description="Valeur nominale moyenne")
    
    # Répartition par pays
    by_country: Dict[Country, Dict[str, Any]] = Field(default_factory=dict)
    
    # Répartition par devise
    by_currency: Dict[Currency, Dict[str, Any]] = Field(default_factory=dict)
    
    # Répartition par niveau de risque
    by_risk_level: Dict[RiskLevel, Dict[str, Any]] = Field(default_factory=dict)
    
    # Répartition par type de produit
    by_product_type: Dict[ProductType, Dict[str, Any]] = Field(default_factory=dict)
    
    # Top émetteurs
    top_issuers: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Statistiques temporelles
    monthly_evolution: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
