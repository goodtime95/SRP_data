"""
Tests pour le projet SRP (Structured Retail Products)
"""
import pytest
import json
import tempfile
import os
from datetime import date
from pathlib import Path

# Ajouter le répertoire parent au path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from projet_SRP.models import (
    SRPProduct, 
    SRPProductList, 
    SRPAnalysis,
    Country, 
    Currency, 
    ProductType, 
    RiskLevel
)
from projet_SRP.data_collector import SRPDataCollector
from projet_SRP.analyzer import SRPAnalyzer
from projet_SRP.utils import (
    generate_sample_srp_data,
    create_sample_json_file,
    validate_srp_data,
    convert_to_srp_products
)

class TestSRPModels:
    """Tests pour les modèles de données"""
    
    def test_srp_product_creation(self):
        """Test de création d'un produit SRP"""
        product = SRPProduct(
            product_id="TEST_001",
            product_name="Test Product",
            issuer="Test Bank",
            country=Country.FRANCE,
            currency=Currency.EUR,
            issue_date=date(2024, 8, 15),
            nominal_value=10000.0,
            product_type=ProductType.BOND,
            risk_level=RiskLevel.MEDIUM
        )
        
        assert product.product_id == "TEST_001"
        assert product.country == Country.FRANCE
        assert product.currency == Currency.EUR
        assert product.nominal_value == 10000.0
    
    def test_srp_product_validation(self):
        """Test de validation des produits SRP"""
        # Test avec valeur nominale négative (doit échouer)
        with pytest.raises(ValueError):
            SRPProduct(
                product_id="TEST_002",
                product_name="Test Product",
                issuer="Test Bank",
                country=Country.FRANCE,
                currency=Currency.EUR,
                issue_date=date(2024, 8, 15),
                nominal_value=-1000.0,  # Valeur négative
                product_type=ProductType.BOND,
                risk_level=RiskLevel.MEDIUM
            )
    
    def test_srp_product_list(self):
        """Test de la liste de produits SRP"""
        product_list = SRPProductList()
        
        # Ajouter des produits
        product1 = SRPProduct(
            product_id="TEST_001",
            product_name="Test Product 1",
            issuer="Test Bank",
            country=Country.FRANCE,
            currency=Currency.EUR,
            issue_date=date(2024, 8, 15),
            nominal_value=10000.0,
            product_type=ProductType.BOND,
            risk_level=RiskLevel.MEDIUM
        )
        
        product2 = SRPProduct(
            product_id="TEST_002",
            product_name="Test Product 2",
            issuer="Test Bank",
            country=Country.BELGIUM,
            currency=Currency.EUR,
            issue_date=date(2024, 8, 16),
            nominal_value=15000.0,
            product_type=ProductType.NOTE,
            risk_level=RiskLevel.LOW
        )
        
        product_list.add_product(product1)
        product_list.add_product(product2)
        
        assert product_list.total_count == 2
        assert len(product_list.countries) == 2
        assert len(product_list.currencies) == 1  # Les deux sont en EUR
        
        # Test des filtres
        french_products = product_list.get_products_by_country(Country.FRANCE)
        assert len(french_products) == 1
        assert french_products[0].product_id == "TEST_001"

class TestSRPDataCollector:
    """Tests pour le collecteur de données"""
    
    def test_collector_initialization(self):
        """Test d'initialisation du collecteur"""
        collector = SRPDataCollector()
        assert collector is not None
        assert hasattr(collector, 'session')
    
    def test_collect_from_file(self):
        """Test de collecte depuis un fichier"""
        # Créer des données de test
        test_data = {
            "products": [
                {
                    "id": "TEST_001",
                    "name": "Test Product",
                    "issuer": "Test Bank",
                    "country": "FR",
                    "currency": "EUR",
                    "issue_date": "2024-08-15",
                    "nominal_value": 10000,
                    "type": "bond",
                    "risk": "3"
                }
            ]
        }
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            collector = SRPDataCollector()
            products = collector.collect_from_file(temp_file)
            
            assert len(products.products) == 1
            assert products.products[0].product_id == "TEST_001"
            assert products.products[0].country == Country.FRANCE
            
        finally:
            # Nettoyer le fichier temporaire
            os.unlink(temp_file)
    
    def test_save_to_file(self):
        """Test de sauvegarde dans un fichier"""
        # Créer des produits de test
        product = SRPProduct(
            product_id="TEST_001",
            product_name="Test Product",
            issuer="Test Bank",
            country=Country.FRANCE,
            currency=Currency.EUR,
            issue_date=date(2024, 8, 15),
            nominal_value=10000.0,
            product_type=ProductType.BOND,
            risk_level=RiskLevel.MEDIUM
        )
        
        product_list = SRPProductList()
        product_list.add_product(product)
        
        # Sauvegarder
        collector = SRPDataCollector()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            collector.save_to_file(temp_file, product_list)
            
            # Vérifier que le fichier a été créé
            assert os.path.exists(temp_file)
            
            # Vérifier le contenu
            with open(temp_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data['total_count'] == 1
            assert len(saved_data['products']) == 1
            
        finally:
            # Nettoyer
            if os.path.exists(temp_file):
                os.unlink(temp_file)

class TestSRPAnalyzer:
    """Tests pour l'analyseur de données"""
    
    def test_analyzer_initialization(self):
        """Test d'initialisation de l'analyseur"""
        analyzer = SRPAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analysis')
    
    def test_analyze_empty_products(self):
        """Test d'analyse avec une liste vide"""
        analyzer = SRPAnalyzer()
        analysis = analyzer.analyze_products(SRPProductList())
        
        assert analysis.total_products == 0
        assert analysis.total_value == 0
    
    def test_analyze_products(self):
        """Test d'analyse de produits"""
        # Créer des produits de test
        product1 = SRPProduct(
            product_id="TEST_001",
            product_name="Test Product 1",
            issuer="Test Bank A",
            country=Country.FRANCE,
            currency=Currency.EUR,
            issue_date=date(2024, 8, 15),
            nominal_value=10000.0,
            product_type=ProductType.BOND,
            risk_level=RiskLevel.MEDIUM
        )
        
        product2 = SRPProduct(
            product_id="TEST_002",
            product_name="Test Product 2",
            issuer="Test Bank B",
            country=Country.BELGIUM,
            currency=Currency.USD,
            issue_date=date(2024, 8, 16),
            nominal_value=15000.0,
            product_type=ProductType.NOTE,
            risk_level=RiskLevel.LOW
        )
        
        product_list = SRPProductList()
        product_list.add_product(product1)
        product_list.add_product(product2)
        
        # Analyser
        analyzer = SRPAnalyzer()
        analysis = analyzer.analyze_products(product_list)
        
        assert analysis.total_products == 2
        assert analysis.total_value == 25000.0
        assert analysis.average_nominal_value == 12500.0
        
        # Vérifier les analyses par pays
        assert len(analysis.by_country) == 2
        assert analysis.by_country[Country.FRANCE]['count'] == 1
        assert analysis.by_country[Country.BELGIUM]['count'] == 1
    
    def test_filtered_products(self):
        """Test du filtrage des produits"""
        # Créer des produits de test
        product1 = SRPProduct(
            product_id="TEST_001",
            product_name="Test Product 1",
            issuer="Test Bank A",
            country=Country.FRANCE,
            currency=Currency.EUR,
            issue_date=date(2024, 8, 15),
            nominal_value=10000.0,
            product_type=ProductType.BOND,
            risk_level=RiskLevel.MEDIUM
        )
        
        product2 = SRPProduct(
            product_id="TEST_002",
            product_name="Test Product 2",
            issuer="Test Bank B",
            country=Country.BELGIUM,
            currency=Currency.USD,
            issue_date=date(2024, 8, 16),
            nominal_value=15000.0,
            product_type=ProductType.NOTE,
            risk_level=RiskLevel.LOW
        )
        
        product_list = SRPProductList()
        product_list.add_product(product1)
        product_list.add_product(product2)
        
        analyzer = SRPAnalyzer()
        analyzer.analyze_products(product_list)
        
        # Tester les filtres
        french_products = analyzer.get_filtered_products({"country": "FR"})
        assert len(french_products) == 1
        assert french_products[0].country == Country.FRANCE
        
        usd_products = analyzer.get_filtered_products({"currency": "USD"})
        assert len(usd_products) == 1
        assert usd_products[0].currency == Currency.USD
        
        low_risk_products = analyzer.get_filtered_products({"risk_level": "2"})
        assert len(low_risk_products) == 1
        assert low_risk_products[0].risk_level == RiskLevel.LOW

class TestSRPUtils:
    """Tests pour les utilitaires"""
    
    def test_generate_sample_data(self):
        """Test de génération de données de test"""
        start_date = date(2024, 8, 15)
        end_date = date(2024, 8, 20)
        
        products = generate_sample_srp_data(10, start_date, end_date)
        
        assert len(products) == 10
        
        for product in products:
            assert 'id' in product
            assert 'name' in product
            assert 'issuer' in product
            assert 'country' in product
            assert 'currency' in product
            assert 'issue_date' in product
            assert 'nominal_value' in product
    
    def test_validate_srp_data(self):
        """Test de validation des données"""
        # Données valides
        valid_data = [
            {
                "id": "TEST_001",
                "name": "Test Product",
                "issuer": "Test Bank",
                "country": "FR",
                "currency": "EUR",
                "issue_date": "2024-08-15",
                "nominal_value": 10000,
                "type": "bond",
                "risk": "3"
            }
        ]
        
        errors = validate_srp_data(valid_data)
        assert len(errors) == 0
        
        # Données invalides
        invalid_data = [
            {
                "id": "TEST_002",
                "name": "",  # Nom vide
                "issuer": "Test Bank",
                "country": "FR",
                "currency": "EUR",
                "issue_date": "2024-08-15",
                "nominal_value": -1000,  # Valeur négative
                "type": "bond",
                "risk": "3"
            }
        ]
        
        errors = validate_srp_data(invalid_data)
        assert len(errors) > 0
    
    def test_convert_to_srp_products(self):
        """Test de conversion des données brutes"""
        raw_data = [
            {
                "id": "TEST_001",
                "name": "Test Product",
                "issuer": "Test Bank",
                "country": "FR",
                "currency": "EUR",
                "issue_date": "2024-08-15",
                "nominal_value": 10000,
                "type": "bond",
                "risk": "3"
            }
        ]
        
        products = convert_to_srp_products(raw_data)
        
        assert len(products) == 1
        assert isinstance(products[0], SRPProduct)
        assert products[0].product_id == "TEST_001"
        assert products[0].country == Country.FRANCE

if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
