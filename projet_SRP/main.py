"""
Script principal pour la collecte et l'analyse des produits SRP
"""
import os
import sys
import logging
import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from config import START_DATE, END_DATE, COUNTRIES, EXPORT_CONFIG
from .data_collector import SRPDataCollector
from .analyzer import SRPAnalyzer
from .models import SRPProductList

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('srp_collection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SRPProcessor:
    """Processeur principal pour la collecte et l'analyse SRP"""
    
    def __init__(self):
        self.collector = SRPDataCollector()
        self.analyzer = SRPAnalyzer()
        self.products = SRPProductList()
        
        # Créer le répertoire de sortie
        os.makedirs(EXPORT_CONFIG["output_dir"], exist_ok=True)
    
    def collect_data(self, start_date: Optional[date] = None, 
                    end_date: Optional[date] = None,
                    countries: Optional[list] = None,
                    from_file: Optional[str] = None) -> SRPProductList:
        """
        Collecte les données SRP
        
        Args:
            start_date: Date de début de collecte
            end_date: Date de fin de collecte
            countries: Liste des pays à collecter
            from_file: Fichier JSON à lire (optionnel)
            
        Returns:
            SRPProductList: Produits collectés
        """
        if from_file and os.path.exists(from_file):
            logger.info(f"Lecture des données depuis le fichier: {from_file}")
            self.products = self.collector.collect_from_file(from_file)
        else:
            logger.info("Collecte des données depuis l'API")
            self.products = self.collector.collect_from_api(
                start_date=start_date,
                end_date=end_date,
                countries=countries
            )
        
        # Sauvegarder les données brutes
        output_file = os.path.join(EXPORT_CONFIG["output_dir"], EXPORT_CONFIG["json_filename"])
        self.collector.save_to_file(output_file, self.products)
        
        return self.products
    
    def analyze_data(self, products: Optional[SRPProductList] = None) -> dict:
        """
        Analyse les données SRP collectées
        
        Args:
            products: Produits à analyser (optionnel)
            
        Returns:
            dict: Résultats de l'analyse
        """
        products = products or self.products
        
        if not products.products:
            logger.warning("Aucun produit à analyser")
            return {}
        
        logger.info(f"Début de l'analyse de {len(products.products)} produits")
        
        # Effectuer l'analyse complète
        analysis = self.analyzer.analyze_products(products)
        
        # Exporter l'analyse au format JSON
        analysis_file = os.path.join(EXPORT_CONFIG["output_dir"], EXPORT_CONFIG["analysis_filename"])
        self.analyzer.export_analysis_to_json(analysis_file)
        
        # Générer le rapport HTML
        report_file = os.path.join(EXPORT_CONFIG["output_dir"], EXPORT_CONFIG["report_filename"])
        self.analyzer.generate_report(report_file)
        
        logger.info("Analyse terminée et exportée")
        
        return analysis.dict()
    
    def run_complete_workflow(self, start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             countries: Optional[list] = None,
                             from_file: Optional[str] = None) -> dict:
        """
        Exécute le workflow complet de collecte et d'analyse
        
        Args:
            start_date: Date de début de collecte
            end_date: Date de fin de collecte
            countries: Liste des pays à collecter
            from_file: Fichier JSON à lire (optionnel)
            
        Returns:
            dict: Résultats complets
        """
        logger.info("=== Début du workflow SRP ===")
        
        # Étape 1: Collecte des données
        products = self.collect_data(start_date, end_date, countries, from_file)
        
        if not products.products:
            logger.error("Aucune donnée collectée. Arrêt du workflow.")
            return {}
        
        # Étape 2: Analyse des données
        analysis = self.analyze_data(products)
        
        # Étape 3: Résumé des résultats
        self._print_summary(products, analysis)
        
        logger.info("=== Workflow SRP terminé ===")
        
        return {
            "products": products.dict(),
            "analysis": analysis
        }
    
    def _print_summary(self, products: SRPProductList, analysis: dict):
        """Affiche un résumé des résultats"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE L'ANALYSE SRP")
        print("="*60)
        
        print(f"🔢 Total des produits collectés: {len(products.products):,}")
        print(f"💰 Valeur nominale totale: {analysis.get('total_value', 0):,.0f} €")
        print(f"📅 Période: {START_DATE.strftime('%d/%m/%Y')} - {END_DATE.strftime('%d/%m/%Y')}")
        print(f"🌍 Pays analysés: {', '.join(COUNTRIES)}")
        
        if analysis.get('by_country'):
            print("\n📈 Répartition par pays:")
            for country, stats in analysis['by_country'].items():
                print(f"   {country}: {stats['count']} produits, "
                      f"{stats['total_value']:,.0f} €")
        
        if analysis.get('top_issuers'):
            print(f"\n🏦 Top émetteur: {analysis['top_issuers'][0]['issuer']} "
                  f"({analysis['top_issuers'][0]['count']} produits)")
        
        print(f"\n💾 Fichiers générés dans: {EXPORT_CONFIG['output_dir']}")
        print("="*60)

def main():
    """Fonction principale du script"""
    parser = argparse.ArgumentParser(description="Collecte et analyse des produits SRP")
    
    parser.add_argument(
        "--start-date",
        type=str,
        help="Date de début (format: YYYY-MM-DD)",
        default=START_DATE.isoformat()
    )
    
    parser.add_argument(
        "--end-date", 
        type=str,
        help="Date de fin (format: YYYY-MM-DD)",
        default=END_DATE.isoformat()
    )
    
    parser.add_argument(
        "--countries",
        nargs="+",
        help="Pays à analyser (codes ISO)",
        default=COUNTRIES
    )
    
    parser.add_argument(
        "--from-file",
        type=str,
        help="Fichier JSON à analyser (au lieu de l'API)"
    )
    
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Collecter uniquement les données (pas d'analyse)"
    )
    
    parser.add_argument(
        "--analyze-only",
        type=str,
        help="Analyser uniquement un fichier JSON existant"
    )
    
    args = parser.parse_args()
    
    try:
        # Parser les dates
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        
        processor = SRPProcessor()
        
        if args.analyze_only:
            # Mode analyse uniquement
            logger.info(f"Analyse du fichier: {args.analyze_only}")
            products = processor.collector.collect_from_file(args.analyze_only)
            analysis = processor.analyze_data(products)
            processor._print_summary(products, analysis)
            
        elif args.collect_only:
            # Mode collecte uniquement
            logger.info("Mode collecte uniquement")
            products = processor.collect_data(start_date, end_date, args.countries, args.from_file)
            logger.info(f"Collecte terminée: {len(products.products)} produits")
            
        else:
            # Mode complet
            processor.run_complete_workflow(start_date, end_date, args.countries, args.from_file)
            
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
