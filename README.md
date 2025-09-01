# 📊 Projet SRP - Structured Retail Products

Un projet Python complet pour la collecte et l'analyse des produits SRP (Structured Retail Products) en France et en Belgique depuis le 15 août 2024.

## 🎯 Objectifs

Ce projet permet de :
- **Collecter** les données SRP depuis différentes sources (API, fichiers JSON)
- **Analyser** et extraire les éléments clés des produits
- **Filtrer** les données selon différents critères
- **Générer** des rapports d'analyse en JSON et HTML
- **Visualiser** les données avec des graphiques et statistiques

## 🏗️ Architecture

```
projet_SRP/
├── __init__.py          # Point d'entrée principal
├── models.py            # Modèles de données Pydantic
├── data_collector.py    # Collecteur de données SRP
├── analyzer.py          # Analyseur de données
├── utils.py             # Utilitaires et données de test
└── main.py              # Script principal CLI
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip ou conda

### Installation des dépendances

```bash
# Cloner le projet
git clone <repository-url>
cd projet_SRP

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows :
.venv\Scripts\activate
# macOS/Linux :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Alternative avec conda

```bash
conda create -n projet_SRP python=3.11 -y
conda activate projet_SRP
pip install -r requirements.txt
```

## 📚 Utilisation

### 1. Utilisation basique

```python
from projet_SRP import SRPDataCollector, SRPAnalyzer

# Collecter les données
collector = SRPDataCollector()
products = collector.collect_from_api()

# Analyser les données
analyzer = SRPAnalyzer()
analysis = analyzer.analyze_products(products)

print(f"Total produits: {analysis.total_products}")
print(f"Valeur totale: {analysis.total_value:,.0f} €")
```

### 2. Collecte depuis un fichier JSON

```python
# Collecter depuis un fichier existant
products = collector.collect_from_file("data.json")

# Analyser
analysis = analyzer.analyze_products(products)
```

### 3. Filtrage des données

```python
# Produits français uniquement
french_products = analyzer.get_filtered_products({"country": "FR"})

# Produits à faible risque
low_risk_products = analyzer.get_filtered_products({"risk_level": "1"})

# Produits en EUR
eur_products = analyzer.get_filtered_products({"currency": "EUR"})
```

### 4. Génération de rapports

```python
# Exporter l'analyse en JSON
analyzer.export_analysis_to_json("analysis.json")

# Générer un rapport HTML
analyzer.generate_report("report.html")
```

## 🖥️ Interface en ligne de commande

### Exécution complète

```bash
# Workflow complet (collecte + analyse)
python -m projet_SRP.main

# Avec paramètres personnalisés
python -m projet_SRP.main --start-date 2024-08-15 --end-date 2024-12-31 --countries FR BE
```

### Options disponibles

```bash
python -m projet_SRP.main --help

Options:
  --start-date DATE     Date de début (format: YYYY-MM-DD)
  --end-date DATE       Date de fin (format: YYYY-MM-DD)
  --countries CODES     Pays à analyser (codes ISO)
  --from-file PATH      Fichier JSON à analyser
  --collect-only        Collecter uniquement les données
  --analyze-only PATH   Analyser uniquement un fichier JSON
```

### Exemples d'utilisation

```bash
# Analyser un fichier existant
python -m projet_SRP.main --analyze-only data.json

# Collecter uniquement les données
python -m projet_SRP.main --collect-only --start-date 2024-08-15

# Workflow complet pour la France uniquement
python -m projet_SRP.main --countries FR
```

## 📊 Données de test

Le projet inclut des utilitaires pour générer des données de test :

```python
from projet_SRP.utils import create_sample_json_file, generate_sample_srp_data

# Générer un fichier de test avec 100 produits
create_sample_json_file("test_data.json", count=100)

# Générer des données personnalisées
products = generate_sample_srp_data(
    count=50,
    start_date=date(2024, 8, 15),
    end_date=date(2024, 12, 31)
)
```

## 🔧 Configuration

Le fichier `config.py` centralise la configuration :

```python
# Dates de collecte
START_DATE = date(2024, 8, 15)  # 15 août 2024
END_DATE = date.today()

# Pays analysés
COUNTRIES = ["FR", "BE"]  # France et Belgique

# Configuration API
API_CONFIG = {
    "base_url": "https://api.example.com",
    "api_key": os.getenv("SRP_API_KEY", ""),
    "timeout": 30,
    "max_retries": 3
}
```

## 📈 Fonctionnalités d'analyse

### Statistiques de base
- Nombre total de produits
- Valeur nominale totale et moyenne
- Répartition par pays et devise

### Analyse par critères
- **Pays** : France (FR) et Belgique (BE)
- **Devises** : EUR, USD, GBP, CHF, JPY
- **Types de produits** : Obligations, Notes, Certificats, Warrants, etc.
- **Niveaux de risque** : 1 (Très faible) à 5 (Très élevé)

### Analyses avancées
- Top émetteurs par volume et nombre de produits
- Évolution temporelle mensuelle
- Distribution des risques et valeurs
- Filtrage multi-critères

## 📁 Structure des données

### Modèle SRPProduct

```python
class SRPProduct(BaseModel):
    product_id: str              # Identifiant unique
    product_name: str            # Nom du produit
    issuer: str                  # Émetteur
    country: Country             # Pays d'émission
    currency: Currency           # Devise
    issue_date: date             # Date d'émission
    maturity_date: Optional[date] # Date d'échéance
    nominal_value: float         # Valeur nominale
    coupon_rate: Optional[float] # Taux de coupon
    product_type: ProductType    # Type de produit
    underlying_asset: Optional[str] # Actif sous-jacent
    risk_level: RiskLevel        # Niveau de risque
    rating: Optional[str]        # Rating
    # ... autres champs
```

### Format JSON d'entrée

```json
{
  "products": [
    {
      "id": "SRP_001",
      "name": "Obligation Indexée CAC 40",
      "issuer": "BNP Paribas",
      "country": "FR",
      "currency": "EUR",
      "issue_date": "2024-08-15",
      "nominal_value": 10000,
      "type": "bond",
      "risk": "3"
    }
  ]
}
```

## 🎨 Exemples et démonstrations

### Script d'exemple

```bash
# Exécuter le script d'exemple
python example_usage.py
```

### Notebook Jupyter

```bash
# Lancer Jupyter
jupyter notebook example_notebook.ipynb
```

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install -r requirements-dev.txt

# Exécuter les tests
pytest

# Avec couverture
pytest --cov=projet_SRP
```

## 📊 Sorties générées

Le projet génère plusieurs types de fichiers :

- **`srp_products.json`** : Données brutes collectées
- **`srp_analysis.json`** : Résultats de l'analyse
- **`srp_report.html`** : Rapport d'analyse en HTML
- **`srp_collection.log`** : Logs d'exécution

## 🔍 Filtrage et recherche

### Filtres disponibles

```python
filters = {
    "country": "FR",           # Pays
    "currency": "EUR",         # Devise
    "product_type": "bond",    # Type de produit
    "risk_level": "1",         # Niveau de risque
    "min_nominal_value": 1000, # Valeur minimale
    "max_nominal_value": 50000,# Valeur maximale
    "issuer": "BNP"            # Recherche dans le nom de l'émetteur
}

filtered_products = analyzer.get_filtered_products(filters)
```

## 🚀 Déploiement et production

### Variables d'environnement

```bash
# Configuration de l'API
export SRP_API_BASE_URL="https://api.votre-source.com"
export SRP_API_KEY="votre-clé-api"

# Exécution
python -m projet_SRP.main
```

### Intégration continue

Le projet peut être intégré dans des pipelines CI/CD pour :
- Collecte automatique quotidienne
- Génération de rapports périodiques
- Surveillance des données SRP

## 🤝 Contribution

### Structure du code

- **Modèles** : Utilisation de Pydantic pour la validation
- **Collecte** : Gestion des erreurs et retry automatique
- **Analyse** : Architecture modulaire et extensible
- **Tests** : Couverture complète des fonctionnalités

### Ajout de nouvelles fonctionnalités

1. Créer les modèles dans `models.py`
2. Implémenter la logique dans les classes appropriées
3. Ajouter les tests unitaires
4. Mettre à jour la documentation

## 📚 Documentation API

### SRPDataCollector

```python
collector = SRPDataCollector()

# Collecte depuis l'API
products = collector.collect_from_api(
    start_date=date(2024, 8, 15),
    end_date=date.today(),
    countries=["FR", "BE"]
)

# Collecte depuis un fichier
products = collector.collect_from_file("data.json")

# Sauvegarde
collector.save_to_file("output.json", products)
```

### SRPAnalyzer

```python
analyzer = SRPAnalyzer()

# Analyse complète
analysis = analyzer.analyze_products(products)

# Filtrage
filtered = analyzer.get_filtered_products({"country": "FR"})

# Export
analyzer.export_analysis_to_json("analysis.json")
analyzer.generate_report("report.html")
```

## 🔮 Évolutions futures

- **Sources multiples** : Intégration d'autres sources de données
- **Machine Learning** : Prédiction des tendances et anomalies
- **API REST** : Interface web pour l'analyse
- **Dashboard** : Interface utilisateur interactive
- **Alertes** : Notifications sur les nouveaux produits

## 📞 Support

Pour toute question ou suggestion :
- Ouvrir une issue sur GitHub
- Consulter la documentation des classes et méthodes
- Utiliser le notebook d'exemple pour tester

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Développé par Victor Bontemps**  
*Projet SRP v1.0.0 - Collecte et analyse des produits structurés*
