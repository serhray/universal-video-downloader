from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)
app.secret_key = 'test-key-123'

print("🚀 Iniciando teste básico do Flask...")

@app.route('/')
def index():
    return "<h1>🎉 Flask funcionando!</h1><p>Teste básico bem-sucedido</p>"

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Flask básico funcionando',
        'test': 'OK'
    })

@app.route('/test-template')
def test_template():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>❌ Erro no template:</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    print("📱 Teste básico - Acesse: http://localhost:5000")
    print("✅ Health Check: http://localhost:5000/health")
    print("🧪 Template Test: http://localhost:5000/test-template")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
