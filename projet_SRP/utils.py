"""
Utilitaires pour le projet SRP (Structured Retail Products)
"""
import json
import random
from datetime import date, timedelta
from typing import List, Dict, Any

from .models import SRPProduct, SRPProductList, Country, Currency, ProductType, RiskLevel

def generate_sample_srp_data(count: int = 100, start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
    """
    Génère des données SRP de test
    
    Args:
        count: Nombre de produits à générer
        start_date: Date de début pour la génération
        end_date: Date de fin pour la génération
        
    Returns:
        List[Dict[str, Any]]: Liste de produits SRP de test
    """
    if start_date is None:
        start_date = date(2024, 8, 15)
    if end_date is None:
        end_date = date.today()
    
    # Données de test
    issuers = [
        "BNP Paribas", "Société Générale", "Crédit Agricole", "LCL", "Crédit Mutuel",
        "Banque Populaire", "Caisse d'Épargne", "HSBC France", "Deutsche Bank France",
        "ING Belgique", "KBC Bank", "Belfius Bank", "Argenta Bank", "AXA Bank"
    ]
    
    product_names = [
        "Obligation Indexée Actions Européennes", "Note Structurée CAC 40",
        "Certificat de Performance", "Warrant Call CAC 40", "Note à Coupon Variable",
        "Obligation à Taux Révisable", "Certificat de Dépôt", "Note à Capital Garanti",
        "Warrant Put Euro Stoxx 50", "Obligation Indexée Matières Premières"
    ]
    
    underlying_assets = [
        "CAC 40", "Euro Stoxx 50", "S&P 500", "Actions Européennes", "Matières Premières",
        "Taux d'Intérêt", "Devises", "Actions Asiatiques", "Actions Émergentes", "Indices Sectoriels"
    ]
    
    products = []
    
    for i in range(count):
        # Générer une date aléatoire dans la plage
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        issue_date = start_date + timedelta(days=random_days)
        
        # Maturité entre 1 et 10 ans
        maturity_days = random.randint(365, 3650)
        maturity_date = issue_date + timedelta(days=maturity_days)
        
        # Valeur nominale entre 1000 et 100000
        nominal_value = random.randint(1000, 100000)
        
        # Taux de coupon entre 0 et 8%
        coupon_rate = round(random.uniform(0, 8), 2)
        
        # Pays aléatoire
        country = random.choice(list(Country))
        
        # Devise (majoritairement EUR)
        currency = Currency.EUR if random.random() < 0.8 else random.choice([Currency.USD, Currency.GBP])
        
        # Type de produit
        product_type = random.choice(list(ProductType))
        
        # Niveau de risque
        risk_level = random.choice(list(RiskLevel))
        
        # Rating
        ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", None]
        rating = random.choice(ratings)
        
        # ISIN (format fictif)
        isin = f"FR{random.randint(1000000000000, 9999999999999)}"
        
        product = {
            "id": f"SRP_{i+1:06d}",
            "name": random.choice(product_names),
            "issuer": random.choice(issuers),
            "country": country.value,
            "currency": currency.value,
            "issue_date": issue_date.isoformat(),
            "maturity_date": maturity_date.isoformat(),
            "nominal_value": nominal_value,
            "coupon_rate": coupon_rate,
            "type": product_type.value,
            "underlying": random.choice(underlying_assets),
            "risk": risk_level.value,
            "rating": rating,
            "isin": isin,
            "min_investment": max(1000, nominal_value * 0.1),
            "max_investment": nominal_value * 10,
            "liquidity": random.choice(["Élevée", "Moyenne", "Faible"]),
            "fees": round(random.uniform(0.5, 3.0), 2)
        }
        
        products.append(product)
    
    return products

def create_sample_json_file(output_file: str = "sample_srp_data.json", count: int = 100):
    """
    Crée un fichier JSON avec des données SRP de test
    
    Args:
        output_file: Chemin du fichier de sortie
        count: Nombre de produits à générer
    """
    data = {
        "products": generate_sample_srp_data(count),
        "metadata": {
            "generated_at": date.today().isoformat(),
            "total_count": count,
            "description": "Données de test SRP générées automatiquement"
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Fichier de test créé: {output_file}")
    print(f"Contient {count} produits SRP de test")

def validate_srp_data(data: List[Dict[str, Any]]) -> List[str]:
    """
    Valide les données SRP et retourne une liste d'erreurs
    
    Args:
        data: Liste de produits SRP à valider
        
    Returns:
        List[str]: Liste des erreurs de validation
    """
    errors = []
    
    for i, product in enumerate(data):
        try:
            # Validation des champs obligatoires
            required_fields = ["id", "name", "issuer", "country", "currency", "issue_date", "nominal_value"]
            for field in required_fields:
                if field not in product or not product[field]:
                    errors.append(f"Produit {i+1}: Champ '{field}' manquant ou vide")
            
            # Validation de la valeur nominale
            if "nominal_value" in product:
                try:
                    value = float(product["nominal_value"])
                    if value <= 0:
                        errors.append(f"Produit {i+1}: Valeur nominale doit être positive")
                except (ValueError, TypeError):
                    errors.append(f"Produit {i+1}: Valeur nominale invalide")
            
            # Validation des dates
            if "issue_date" in product:
                try:
                    date.fromisoformat(product["issue_date"])
                except ValueError:
                    errors.append(f"Produit {i+1}: Date d'émission invalide")
            
            if "maturity_date" in product and product["maturity_date"]:
                try:
                    maturity = date.fromisoformat(product["maturity_date"])
                    issue = date.fromisoformat(product["issue_date"])
                    if maturity <= issue:
                        errors.append(f"Produit {i+1}: Date d'échéance doit être postérieure à la date d'émission")
                except ValueError:
                    errors.append(f"Produit {i+1}: Date d'échéance invalide")
            
            # Validation du taux de coupon
            if "coupon_rate" in product and product["coupon_rate"] is not None:
                try:
                    rate = float(product["coupon_rate"])
                    if rate < 0 or rate > 100:
                        errors.append(f"Produit {i+1}: Taux de coupon doit être entre 0 et 100%")
                except (ValueError, TypeError):
                    errors.append(f"Produit {i+1}: Taux de coupon invalide")
            
        except Exception as e:
            errors.append(f"Produit {i+1}: Erreur de validation: {e}")
    
    return errors

def print_srp_summary(products: List[Dict[str, Any]]):
    """
    Affiche un résumé des produits SRP
    
    Args:
        products: Liste des produits SRP
    """
    if not products:
        print("Aucun produit à afficher")
        return
    
    print(f"\n📊 RÉSUMÉ DES PRODUITS SRP ({len(products)} produits)")
    print("="*50)
    
    # Statistiques de base
    total_value = sum(p.get("nominal_value", 0) for p in products)
    avg_value = total_value / len(products) if products else 0
    
    print(f"💰 Valeur nominale totale: {total_value:,.0f} €")
    print(f"📊 Valeur moyenne: {avg_value:,.0f} €")
    
    # Répartition par pays
    countries = {}
    for p in products:
        country = p.get("country", "Inconnu")
        countries[country] = countries.get(country, 0) + 1
    
    print(f"\n🌍 Répartition par pays:")
    for country, count in sorted(countries.items()):
        print(f"   {country}: {count} produits")
    
    # Répartition par devise
    currencies = {}
    for p in products:
        currency = p.get("currency", "Inconnu")
        currencies[currency] = currencies.get(currency, 0) + 1
    
    print(f"\n💰 Répartition par devise:")
    for currency, count in sorted(currencies.items()):
        print(f"   {currency}: {count} produits")
    
    # Top émetteurs
    issuers = {}
    for p in products:
        issuer = p.get("issuer", "Inconnu")
        issuers[issuer] = issuers.get(issuer, 0) + 1
    
    print(f"\n🏦 Top 5 émetteurs:")
    top_issuers = sorted(issuers.items(), key=lambda x: x[1], reverse=True)[:5]
    for issuer, count in top_issuers:
        print(f"   {issuer}: {count} produits")

def convert_to_srp_products(data: List[Dict[str, Any]]) -> List[SRPProduct]:
    """
    Convertit les données brutes en objets SRPProduct
    
    Args:
        data: Liste de dictionnaires de produits
        
    Returns:
        List[SRPProduct]: Liste d'objets SRPProduct
    """
    products = []
    
    for item in data:
        try:
            # Créer l'objet SRPProduct
            product = SRPProduct(
                product_id=item.get("id", str(hash(str(item)))),
                product_name=item.get("name", "Nom inconnu"),
                issuer=item.get("issuer", "Émetteur inconnu"),
                country=Country(item.get("country", "FR")),
                currency=Currency(item.get("currency", "EUR")),
                issue_date=date.fromisoformat(item.get("issue_date", "2024-08-15")),
                maturity_date=date.fromisoformat(item.get("maturity_date")) if item.get("maturity_date") else None,
                nominal_value=float(item.get("nominal_value", 1000)),
                coupon_rate=float(item.get("coupon_rate")) if item.get("coupon_rate") is not None else None,
                product_type=ProductType(item.get("type", "other")),
                underlying_asset=item.get("underlying"),
                risk_level=RiskLevel(item.get("risk", "3")),
                rating=item.get("rating"),
                isin=item.get("isin"),
                cusip=item.get("cusip"),
                min_investment=float(item.get("min_investment")) if item.get("min_investment") else None,
                max_investment=float(item.get("max_investment")) if item.get("max_investment") else None,
                liquidity=item.get("liquidity"),
                fees=float(item.get("fees")) if item.get("fees") else None
            )
            products.append(product)
            
        except Exception as e:
            print(f"Erreur lors de la conversion du produit: {e}")
            continue
    
    return products

if __name__ == "__main__":
    # Créer un fichier de test
    create_sample_json_file("sample_srp_data.json", 50)
    
    # Charger et valider les données
    with open("sample_srp_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get("products", [])
    
    # Valider les données
    errors = validate_srp_data(products)
    if errors:
        print(f"\n❌ Erreurs de validation trouvées ({len(errors)}):")
        for error in errors[:10]:  # Afficher seulement les 10 premières erreurs
            print(f"   {error}")
    else:
        print("\n✅ Aucune erreur de validation trouvée")
    
    # Afficher le résumé
    print_srp_summary(products)
