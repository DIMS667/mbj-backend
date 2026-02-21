import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Variables d'environnement forcées (fallback si .htaccess ne les passe pas)
os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://c2734982c_mbj_user:MbjUser2024@127.0.0.1:5432/c2734982c_mbj_db')
os.environ.setdefault('SECRET_KEY', '8f9539f87b37539c250b35d616066a6aa46c035b9af2f2895b28557eb0c8a8fb')
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '480')
os.environ.setdefault('UPLOAD_DIR', 'uploads')
os.environ.setdefault('MAX_FILE_SIZE_MB', '5')
os.environ.setdefault('APP_NAME', 'MBJ API')
os.environ.setdefault('APP_ENV', 'production')
os.environ.setdefault('ALLOWED_ORIGINS', 'https://lamaisonbleuedejulien.org,https://admin.lamaisonbleuedejulien.org')

from main import app
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(app)

# source ~/virtualenv/public_html/api/3.13/bin/activate
# cd ~/public_html/api
# pip install -r requirements.txt