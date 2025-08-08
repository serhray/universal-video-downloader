import sys
import os
from pathlib import Path

print("🚀 VERCEL API - Iniciando importação...")

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

print(f"📁 VERCEL API - Root dir: {root_dir}")
print(f"📁 VERCEL API - Python path: {sys.path[:3]}")

try:
    print("📥 VERCEL API - Tentando importar app principal...")
    
    # Importar aplicação Flask principal
    from app import app
    
    print("✅ VERCEL API - Flask app importado com sucesso!")
    print(f"🔍 VERCEL API - App name: {app.name}")
    print(f"🔍 VERCEL API - Routes: {len(app.url_map._rules)} rotas")
    
    # Listar algumas rotas para debug
    routes = [str(rule) for rule in app.url_map.iter_rules()][:5]
    print(f"🔍 VERCEL API - Primeiras rotas: {routes}")
    
    # Para Vercel: a aplicação Flask deve ser exportada como 'app'
    # Vercel automaticamente detecta 'app' como aplicação WSGI
    
except ImportError as e:
    print(f"❌ VERCEL API - ImportError: {e}")
    print(f"📁 VERCEL API - Working dir: {os.getcwd()}")
    print(f"📁 VERCEL API - Files in root: {os.listdir(root_dir)}")
    
    # Criar aplicação Flask mínima em caso de erro
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return jsonify({
            'error': f'ImportError: {str(e)}',
            'working_dir': os.getcwd(),
            'root_dir': str(root_dir),
            'python_path': sys.path[:3]
        }), 500
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'error',
            'message': 'Main app failed to import',
            'error': str(e)
        }), 500

except Exception as e:
    print(f"❌ VERCEL API - Exception: {e}")
    import traceback
    traceback.print_exc()
    
    # Criar aplicação Flask mínima em caso de erro
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return jsonify({
            'error': f'Exception: {str(e)}',
            'working_dir': os.getcwd(),
            'root_dir': str(root_dir)
        }), 500
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'error', 
            'message': 'Main app failed to import',
            'error': str(e)
        }), 500

print("🚀 VERCEL API - Configuração concluída!")
