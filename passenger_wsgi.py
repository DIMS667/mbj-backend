# passenger_wsgi.py — Point d'entrée cPanel Passenger pour FastAPI

import sys
import os

# Ajouter le dossier du projet au path Python
sys.path.insert(0, os.path.dirname(__file__))

# Charger les variables d'environnement depuis .env si présent
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

# Importer l'app FastAPI
from main import app

# Adaptateur ASGI → WSGI pour Passenger
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(app)