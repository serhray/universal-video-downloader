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

# Entry point para Vercel
if __name__ == '__main__':
    app.run(debug=True)
