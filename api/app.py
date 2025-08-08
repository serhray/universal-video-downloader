import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    # Importar aplicação Flask principal
    from app import app
    
    print("✅ Flask app imported successfully")
    
    # Para Vercel: a aplicação Flask deve ser exportada como 'app'
    # Vercel automaticamente detecta 'app' como aplicação WSGI
    
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    # Criar aplicação Flask mínima em caso de erro
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Error importing main app: {str(e)}", 500
    
    @app.route('/health')
    def health():
        return "API is running but main app failed to import", 200
