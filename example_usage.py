#!/usr/bin/env python3
"""
Exemple d'utilisation du projet SRP (Structured Retail Products)
Ce script démontre comment utiliser les différents composants du projet
"""

import json
import os
from datetime import date
from pathlib import Path

# Ajouter le répertoire parent au path
import sys
sys.path.append(str(Path(__file__).parent))

from projet_SRP import (
    SRPDataCollector,
    SRPAnalyzer,
    generate_sample_srp_data,
    create_sample_json_file,
    validate_srp_data,
    print_srp_summary
)

def main():
    """Exemple principal d'utilisation"""
    print("🚀 EXEMPLE D'UTILISATION DU PROJET SRP")
    print("=" * 50)
    
    # 1. Génération de données de test
    print("\n1️⃣ Génération de données de test...")
    sample_file = "sample_srp_data.json"
    create_sample_json_file(sample_file, count=50)
    
    # 2. Validation des données
    print("\n2️⃣ Validation des données...")
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get("products", [])
    errors = validate_srp_data(products)
    
    if errors:
        print(f"❌ {len(errors)} erreurs de validation trouvées")
        for error in errors[:3]:  # Afficher seulement les 3 premières
            print(f"   {error}")
    else:
        print("✅ Aucune erreur de validation")
    
    # 3. Affichage du résumé
    print("\n3️⃣ Résumé des données...")
    print_srp_summary(products)
    
    # 4. Collecte des données (depuis le fichier)
    print("\n4️⃣ Collecte des données...")
    collector = SRPDataCollector()
    srp_products = collector.collect_from_file(sample_file)
    
    print(f"📊 {len(srp_products.products)} produits collectés")
    
    # 5. Analyse des données
    print("\n5️⃣ Analyse des données...")
    analyzer = SRPAnalyzer()
    analysis = analyzer.analyze_products(srp_products)
    
    print(f"📈 Analyse terminée:")
    print(f"   - Total produits: {analysis.total_products}")
    print(f"   - Valeur totale: {analysis.total_value:,.0f} €")
    print(f"   - Valeur moyenne: {analysis.average_nominal_value:,.0f} €")
    
    # 6. Filtrage des produits
    print("\n6️⃣ Filtrage des produits...")
    
    # Produits français uniquement
    french_products = analyzer.get_filtered_products({"country": "FR"})
    print(f"🇫🇷 Produits français: {len(french_products)}")
    
    # Produits belges uniquement
    belgian_products = analyzer.get_filtered_products({"country": "BE"})
    print(f"🇧🇪 Produits belges: {len(belgian_products)}")
    
    # Produits à faible risque
    low_risk_products = analyzer.get_filtered_products({"risk_level": "1"})
    print(f"🟢 Produits à faible risque: {len(low_risk_products)}")
    
    # Produits en EUR
    eur_products = analyzer.get_filtered_products({"currency": "EUR"})
    print(f"💶 Produits en EUR: {len(eur_products)}")
    
    # 7. Export des résultats
    print("\n7️⃣ Export des résultats...")
    
    # Créer le répertoire de sortie
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder l'analyse
    analysis_file = os.path.join(output_dir, "srp_analysis.json")
    analyzer.export_analysis_to_json(analysis_file)
    print(f"📄 Analyse exportée: {analysis_file}")
    
    # Générer le rapport HTML
    report_file = os.path.join(output_dir, "srp_report.html")
    analyzer.generate_report(report_file)
    print(f"🌐 Rapport HTML généré: {report_file}")
    
    # 8. Statistiques détaillées
    print("\n8️⃣ Statistiques détaillées...")
    
    if analysis.by_country:
        print("\n📊 Répartition par pays:")
        for country, stats in analysis.by_country.items():
            print(f"   {country.value}: {stats['count']} produits, "
                  f"{stats['total_value']:,.0f} €")
    
    if analysis.by_currency:
        print("\n💰 Répartition par devise:")
        for currency, stats in analysis.by_currency.items():
            print(f"   {currency.value}: {stats['count']} produits, "
                  f"{stats['total_value']:,.0f} €")
    
    if analysis.top_issuers:
        print("\n🏦 Top 3 émetteurs:")
        for i, issuer in enumerate(analysis.top_issuers[:3], 1):
            print(f"   {i}. {issuer['issuer']}: {issuer['count']} produits, "
                  f"{issuer['total_value']:,.0f} €")
    
    print("\n✅ Exemple terminé avec succès!")
    print(f"📁 Fichiers générés dans le répertoire: {output_dir}")

def demo_advanced_features():
    """Démonstration des fonctionnalités avancées"""
    print("\n🔧 DÉMONSTRATION DES FONCTIONNALITÉS AVANCÉES")
    print("=" * 50)
    
    # Créer des données de test avec des paramètres spécifiques
    start_date = date(2024, 8, 15)
    end_date = date(2024, 12, 31)
    
    print(f"📅 Génération de données du {start_date} au {end_date}...")
    
    # Générer des données avec des paramètres spécifiques
    custom_products = generate_sample_srp_data(
        count=25,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"📊 {len(custom_products)} produits générés")
    
    # Analyser ces données
    analyzer = SRPAnalyzer()
    
    # Convertir en objets SRPProduct
    from projet_SRP.utils import convert_to_srp_products
    srp_products = convert_to_srp_products(custom_products)
    
    # Créer une liste de produits
    from projet_SRP.models import SRPProductList
    product_list = SRPProductList()
    for product in srp_products:
        product_list.add_product(product)
    
    # Analyser
    analysis = analyzer.analyze_products(product_list)
    
    print(f"📈 Analyse des données personnalisées:")
    print(f"   - Période: {start_date} - {end_date}")
    print(f"   - Produits: {analysis.total_products}")
    print(f"   - Valeur totale: {analysis.total_value:,.0f} €")
    
    # Afficher l'évolution temporelle
    if analysis.monthly_evolution:
        print("\n📅 Évolution mensuelle:")
        for month, stats in sorted(analysis.monthly_evolution.items()):
            print(f"   {month}: {stats['count']} produits, "
                  f"{stats['total_value']:,.0f} €")

if __name__ == "__main__":
    try:
        main()
        demo_advanced_features()
        
        print("\n🎉 Toutes les démonstrations terminées!")
        print("\n📚 Pour plus d'informations, consultez:")
        print("   - Le README.md")
        print("   - Les docstrings des classes et méthodes")
        print("   - Le notebook Jupyter example_notebook.ipynb")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()
