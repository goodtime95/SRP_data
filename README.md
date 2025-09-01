# projet_SRP

Mini squelette de projet Python.

## Installation (venv nommé comme le projet)

```bash
cd projet_SRP
python -m venv projet_SRP
# Activation
# macOS/Linux :
source projet_SRP/bin/activate
# Windows :
projet_SRP\Scripts\activate
pip install -r requirements.txt
```

### Alternative : conda
```bash
conda create -n projet_SRP python=3.11 -y
conda activate projet_SRP
pip install -r requirements.txt
```

## Exécution
```bash
python -m projet_SRP
```

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```
