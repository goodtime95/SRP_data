"""
Module d'analyse des données SRP (Structured Retail Products)
"""
import json
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import pandas as pd
import numpy as np

from .models import SRPProduct, SRPProductList, SRPAnalysis, Country, Currency, ProductType, RiskLevel
from config import ANALYSIS_FILTERS

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SRPAnalyzer:
    """Analyseur de données SRP pour extraire les éléments clés"""
    
    def __init__(self, products: SRPProductList = None):
        self.products = products or SRPProductList()
        self.analysis = SRPAnalysis()
    
    def analyze_products(self, products: SRPProductList = None) -> SRPAnalysis:
        """
        Analyse complète des produits SRP
        
        Args:
            products: Liste des produits à analyser
            
        Returns:
            SRPAnalysis: Résultats de l'analyse
        """
        self.products = products or self.products
        
        if not self.products.products:
            logger.warning("Aucun produit à analyser")
            return self.analysis
        
        logger.info(f"Début de l'analyse de {len(self.products.products)} produits SRP")
        
        # Analyses de base
        self._analyze_basic_stats()
        self._analyze_by_country()
        self._analyze_by_currency()
        self._analyze_by_risk_level()
        self._analyze_by_product_type()
        self._analyze_top_issuers()
        self._analyze_temporal_evolution()
        
        logger.info("Analyse terminée")
        return self.analysis
    
    def _analyze_basic_stats(self):
        """Analyse des statistiques de base"""
        products = self.products.products
        
        self.analysis.total_products = len(products)
        self.analysis.total_value = sum(p.nominal_value for p in products)
        
        if products:
            self.analysis.average_nominal_value = self.analysis.total_value / len(products)
        
        logger.info(f"Statistiques de base: {self.analysis.total_products} produits, "
                   f"valeur totale: {self.analysis.total_value:,.2f}")
    
    def _analyze_by_country(self):
        """Analyse par pays"""
        products = self.products.products
        
        for country in Country:
            country_products = [p for p in products if p.country == country]
            
            if country_products:
                country_stats = {
                    "count": len(country_products),
                    "total_value": sum(p.nominal_value for p in country_products),
                    "average_value": sum(p.nominal_value for p in country_products) / len(country_products),
                    "currencies": list(set(p.currency.value for p in country_products)),
                    "product_types": list(set(p.product_type.value for p in country_products)),
                    "risk_distribution": Counter(p.risk_level.value for p in country_products),
                    "top_issuers": self._get_top_issuers(country_products, limit=5)
                }
                
                self.analysis.by_country[country] = country_stats
        
        logger.info(f"Analyse par pays terminée: {len(self.analysis.by_country)} pays analysés")
    
    def _analyze_by_currency(self):
        """Analyse par devise"""
        products = self.products.products
        
        for currency in Currency:
            currency_products = [p for p in products if p.currency == currency]
            
            if currency_products:
                currency_stats = {
                    "count": len(currency_products),
                    "total_value": sum(p.nominal_value for p in currency_products),
                    "average_value": sum(p.nominal_value for p in currency_products) / len(currency_products),
                    "countries": list(set(p.country.value for p in currency_products)),
                    "product_types": list(set(p.product_type.value for p in currency_products)),
                    "risk_distribution": Counter(p.risk_level.value for p in currency_products)
                }
                
                self.analysis.by_currency[currency] = currency_stats
        
        logger.info(f"Analyse par devise terminée: {len(self.analysis.by_currency)} devises analysées")
    
    def _analyze_by_risk_level(self):
        """Analyse par niveau de risque"""
        products = self.products.products
        
        for risk_level in RiskLevel:
            risk_products = [p for p in products if p.risk_level == risk_level]
            
            if risk_products:
                risk_stats = {
                    "count": len(risk_products),
                    "total_value": sum(p.nominal_value for p in risk_products),
                    "average_value": sum(p.nominal_value for p in risk_products) / len(risk_products),
                    "countries": list(set(p.country.value for p in risk_products)),
                    "currencies": list(set(p.currency.value for p in risk_products)),
                    "product_types": list(set(p.product_type.value for p in risk_products)),
                    "top_issuers": self._get_top_issuers(risk_products, limit=3)
                }
                
                self.analysis.by_risk_level[risk_level] = risk_stats
        
        logger.info(f"Analyse par niveau de risque terminée: {len(self.analysis.by_risk_level)} niveaux analysés")
    
    def _analyze_by_product_type(self):
        """Analyse par type de produit"""
        products = self.products.products
        
        for product_type in ProductType:
            type_products = [p for p in products if p.product_type == product_type]
            
            if type_products:
                type_stats = {
                    "count": len(type_products),
                    "total_value": sum(p.nominal_value for p in type_products),
                    "average_value": sum(p.nominal_value for p in type_products) / len(type_products),
                    "countries": list(set(p.country.value for p in type_products)),
                    "currencies": list(set(p.currency.value for p in type_products)),
                    "risk_distribution": Counter(p.risk_level.value for p in type_products),
                    "average_coupon": self._calculate_average_coupon(type_products)
                }
                
                self.analysis.by_product_type[product_type] = type_stats
        
        logger.info(f"Analyse par type de produit terminée: {len(self.analysis.by_product_type)} types analysés")
    
    def _analyze_top_issuers(self):
        """Analyse des principaux émetteurs"""
        products = self.products.products
        
        # Grouper par émetteur
        issuer_stats = defaultdict(lambda: {
            "count": 0,
            "total_value": 0,
            "countries": set(),
            "currencies": set(),
            "product_types": set()
        })
        
        for product in products:
            issuer = product.issuer
            issuer_stats[issuer]["count"] += 1
            issuer_stats[issuer]["total_value"] += product.nominal_value
            issuer_stats[issuer]["countries"].add(product.country.value)
            issuer_stats[issuer]["currencies"].add(product.currency.value)
            issuer_stats[issuer]["product_types"].add(product.product_type.value)
        
        # Convertir en liste et trier par valeur totale
        top_issuers = []
        for issuer, stats in issuer_stats.items():
            top_issuers.append({
                "issuer": issuer,
                "count": stats["count"],
                "total_value": stats["total_value"],
                "average_value": stats["total_value"] / stats["count"],
                "countries": list(stats["countries"]),
                "currencies": list(stats["currencies"]),
                "product_types": list(stats["product_types"])
            })
        
        # Trier par valeur totale décroissante
        top_issuers.sort(key=lambda x: x["total_value"], reverse=True)
        self.analysis.top_issuers = top_issuers[:10]  # Top 10
        
        logger.info(f"Analyse des émetteurs terminée: {len(self.analysis.top_issuers)} émetteurs analysés")
    
    def _analyze_temporal_evolution(self):
        """Analyse de l'évolution temporelle"""
        products = self.products.products
        
        # Grouper par mois
        monthly_stats = defaultdict(lambda: {
            "count": 0,
            "total_value": 0,
            "countries": set(),
            "currencies": set()
        })
        
        for product in products:
            month_key = f"{product.issue_date.year}-{product.issue_date.month:02d}"
            monthly_stats[month_key]["count"] += 1
            monthly_stats[month_key]["total_value"] += product.nominal_value
            monthly_stats[month_key]["countries"].add(product.country.value)
            monthly_stats[month_key]["currencies"].add(product.currency.value)
        
        # Convertir en format final
        for month, stats in monthly_stats.items():
            self.analysis.monthly_evolution[month] = {
                "count": stats["count"],
                "total_value": stats["total_value"],
                "average_value": stats["total_value"] / stats["count"] if stats["count"] > 0 else 0,
                "countries": list(stats["countries"]),
                "currencies": list(stats["currencies"])
            }
        
        logger.info(f"Analyse temporelle terminée: {len(self.analysis.monthly_evolution)} mois analysés")
    
    def _get_top_issuers(self, products: List[SRPProduct], limit: int = 5) -> List[Dict[str, Any]]:
        """Récupère les principaux émetteurs pour une liste de produits"""
        issuer_counts = Counter(p.issuer for p in products)
        return [{"issuer": issuer, "count": count} for issuer, count in issuer_counts.most_common(limit)]
    
    def _calculate_average_coupon(self, products: List[SRPProduct]) -> Optional[float]:
        """Calcule le taux de coupon moyen pour une liste de produits"""
        coupons = [p.coupon_rate for p in products if p.coupon_rate is not None]
        return sum(coupons) / len(coupons) if coupons else None
    
    def get_products_summary(self) -> Dict[str, Any]:
        """Récupère un résumé des produits"""
        if not self.products.products:
            return {}
        
        products = self.products.products
        
        summary = {
            "total_count": len(products),
            "date_range": {
                "start": min(p.issue_date for p in products).isoformat(),
                "end": max(p.issue_date for p in products).isoformat()
            },
            "countries": list(set(p.country.value for p in products)),
            "currencies": list(set(p.currency.value for p in products)),
            "product_types": list(set(p.product_type.value for p in products)),
            "risk_levels": list(set(p.risk_level.value for p in products)),
            "total_nominal_value": sum(p.nominal_value for p in products),
            "average_nominal_value": sum(p.nominal_value for p in products) / len(products)
        }
        
        return summary
    
    def get_filtered_products(self, filters: Dict[str, Any] = None) -> List[SRPProduct]:
        """
        Récupère les produits filtrés selon des critères
        
        Args:
            filters: Dictionnaire de filtres à appliquer
            
        Returns:
            List[SRPProduct]: Produits filtrés
        """
        filters = filters or {}
        products = self.products.products
        
        # Filtres disponibles
        if "country" in filters:
            products = [p for p in products if p.country.value == filters["country"]]
        
        if "currency" in filters:
            products = [p for p in products if p.currency.value == filters["currency"]]
        
        if "product_type" in filters:
            products = [p for p in products if p.product_type.value == filters["product_type"]]
        
        if "risk_level" in filters:
            products = [p for p in products if p.risk_level.value == filters["risk_level"]]
        
        if "min_nominal_value" in filters:
            products = [p for p in products if p.nominal_value >= filters["min_nominal_value"]]
        
        if "max_nominal_value" in filters:
            products = [p for p in products if p.nominal_value <= filters["max_nominal_value"]]
        
        if "issuer" in filters:
            products = [p for p in products if filters["issuer"].lower() in p.issuer.lower()]
        
        return products
    
    def export_analysis_to_json(self, file_path: str):
        """Exporte l'analyse au format JSON"""
        try:
            # Conversion en format JSON compatible
            data = self.analysis.dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Analyse exportée dans {file_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export de l'analyse: {e}")
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Génère un rapport d'analyse en HTML
        
        Args:
            output_file: Fichier de sortie (optionnel)
            
        Returns:
            str: Contenu du rapport HTML
        """
        if not self.analysis.total_products:
            return "<p>Aucune donnée à analyser</p>"
        
        html_content = self._generate_html_report()
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Rapport généré dans {output_file}")
            except Exception as e:
                logger.error(f"Erreur lors de la génération du rapport: {e}")
        
        return html_content
    
    def _generate_html_report(self) -> str:
        """Génère le contenu HTML du rapport"""
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rapport d'analyse SRP</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-card {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Rapport d'analyse des produits SRP</h1>
                <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>📈 Statistiques générales</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{self.analysis.total_products:,}</div>
                        <div class="stat-label">Total produits</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{self.analysis.total_value:,.0f} €</div>
                        <div class="stat-label">Valeur totale</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{self.analysis.average_nominal_value:,.0f} €</div>
                        <div class="stat-label">Valeur moyenne</div>
                    </div>
                </div>
            </div>
        """
        
        # Ajouter les sections d'analyse
        if self.analysis.by_country:
            html += self._generate_country_section()
        
        if self.analysis.by_currency:
            html += self._generate_currency_section()
        
        if self.analysis.by_risk_level:
            html += self._generate_risk_section()
        
        if self.analysis.top_issuers:
            html += self._generate_issuers_section()
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _generate_country_section(self) -> str:
        """Génère la section d'analyse par pays"""
        html = """
            <div class="section">
                <h2>🌍 Analyse par pays</h2>
        """
        
        for country, stats in self.analysis.by_country.items():
            html += f"""
                <h3>{country.value}</h3>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{stats['count']}</div>
                        <div class="stat-label">Produits</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['total_value']:,.0f} €</div>
                        <div class="stat-label">Valeur totale</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['average_value']:,.0f} €</div>
                        <div class="stat-label">Valeur moyenne</div>
                    </div>
                </div>
            """
        
        html += "</div>"
        return html
    
    def _generate_currency_section(self) -> str:
        """Génère la section d'analyse par devise"""
        html = """
            <div class="section">
                <h2>💰 Analyse par devise</h2>
        """
        
        for currency, stats in self.analysis.by_currency.items():
            html += f"""
                <h3>{currency.value}</h3>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{stats['count']}</div>
                        <div class="stat-label">Produits</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['total_value']:,.0f}</div>
                        <div class="stat-label">Valeur totale</div>
                    </div>
                </div>
            """
        
        html += "</div>"
        return html
    
    def _generate_risk_section(self) -> str:
        """Génère la section d'analyse par niveau de risque"""
        html = """
            <div class="section">
                <h2>⚠️ Analyse par niveau de risque</h2>
        """
        
        for risk_level, stats in self.analysis.by_risk_level.items():
            risk_labels = {
                "1": "Très faible",
                "2": "Faible", 
                "3": "Moyen",
                "4": "Élevé",
                "5": "Très élevé"
            }
            
            html += f"""
                <h3>Niveau {risk_level.value} - {risk_labels.get(risk_level.value, 'Inconnu')}</h3>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{stats['count']}</div>
                        <div class="stat-label">Produits</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['total_value']:,.0f} €</div>
                        <div class="stat-label">Valeur totale</div>
                    </div>
                </div>
            """
        
        html += "</div>"
        return html
    
    def _generate_issuers_section(self) -> str:
        """Génère la section des principaux émetteurs"""
        html = """
            <div class="section">
                <h2>🏦 Principaux émetteurs</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Émetteur</th>
                            <th>Nombre de produits</th>
                            <th>Valeur totale</th>
                            <th>Valeur moyenne</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for issuer in self.analysis.top_issuers[:10]:
            html += f"""
                <tr>
                    <td>{issuer['issuer']}</td>
                    <td>{issuer['count']}</td>
                    <td>{issuer['total_value']:,.0f} €</td>
                    <td>{issuer['average_value']:,.0f} €</td>
                </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        """
        return html
