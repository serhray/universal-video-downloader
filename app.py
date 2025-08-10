from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    """Página principal - teste básico"""
    try:
        return render_template('index.html', cache_bust='123456')
    except Exception as e:
        return f"<h1>🚀 Universal Video Downloader</h1><p>Template error: {str(e)}</p><p>Plataformas: Instagram, Facebook, TikTok, X/Twitter</p>"

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Universal Video Downloader',
        'platforms': ['Instagram', 'Facebook', 'TikTok', 'X/Twitter'],
        'version': '2.0.0'
    })

@app.route('/test')
def test():
    """Endpoint de teste"""
    return jsonify({
        'message': 'Flask funcionando no Vercel!',
        'platforms': ['Instagram', 'Facebook', 'TikTok', 'X/Twitter'],
        'status': 'working'
    })

@app.route('/privacy-policy')
def privacy_policy():
    """Página de política de privacidade"""
    try:
        return render_template('privacy-policy.html')
    except:
        return "<h1>Política de Privacidade</h1><p>Em desenvolvimento</p>"

@app.route('/terms')
@app.route('/terms-of-service')
def terms_of_service():
    """Página de termos de uso"""
    try:
        return render_template('terms-of-service.html')
    except:
        return "<h1>Termos de Uso</h1><p>Em desenvolvimento</p>"

@app.route('/about')
def about():
    """Página sobre o projeto"""
    try:
        return render_template('about.html')
    except:
        return "<h1>Sobre</h1><p>Universal Video Downloader - Instagram, Facebook, TikTok, X/Twitter</p>"

# Entry point para Vercel
if __name__ == '__main__':
    app.run(debug=True)
