import sys
import os

# Adicionar o diretório raiz ao path para importar app.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar a aplicação Flask do arquivo principal
from app import app

# Função handler para Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

# Para compatibilidade com Vercel
if __name__ == "__main__":
    app.run()
