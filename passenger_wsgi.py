import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    from main import app
    from a2wsgi import ASGIMiddleware
    application = ASGIMiddleware(app)
except Exception as e:
    error_msg = traceback.format_exc()
    def application(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [f"ERREUR:\n{error_msg}".encode()]

# source ~/virtualenv/mbj-backend/3.13/bin/activate
# cd ~/mbj-backend
# alembic upgrade head