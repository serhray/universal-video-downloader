import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Importar aplicação Flask principal
from app import app

# Para Vercel: exportar a aplicação Flask diretamente
# O Vercel automaticamente detecta 'app' como aplicação WSGI
application = app

# Handler para Vercel (compatibilidade)
def handler(event, context):
    return app(event, context)
