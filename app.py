from flask import Flask, jsonify, render_template, request, send_file
import yt_dlp
import os
import tempfile
import uuid
from datetime import datetime
import re

app = Flask(__name__)

# Configuração global para downloads
DOWNLOAD_DIR = tempfile.gettempdir()
download_cache = {}

def get_ydl_opts(platform, quality='best'):
    """Configurações otimizadas do yt-dlp por plataforma"""
    base_opts = {
        'format': 'best[height<=720]/best',
        'noplaylist': True,
        'extract_flat': False,
        'writethumbnail': False,
        'writeinfojson': False,
        'ignoreerrors': True,
        'no_warnings': False,
        'quiet': False,
    }
    
    # Configurações específicas por plataforma
    if platform == 'Instagram':
        base_opts.update({
            'format': 'best[height<=720]/best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        })
    elif platform == 'Facebook':
        base_opts.update({
            'format': 'best[height<=1080]/best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        })
    elif platform == 'TikTok':
        base_opts.update({
            'format': 'best[height<=720]/best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        })
    elif platform == 'X/Twitter':
        base_opts.update({
            'format': 'best[height<=720]/best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://twitter.com/',
                'X-Requested-With': 'XMLHttpRequest',
            },
            'extractor_args': {
                'twitter': {
                    'legacy_api': True,
                }
            },
            'geo_bypass': True,
            'geo_bypass_country': 'US'
        })
    
    return base_opts

@app.route('/')
def index():
    """Página principal"""
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
        'version': '2.0.0',
        'yt_dlp': 'enabled'
    })

@app.route('/api/validate_url', methods=['POST'])
def validate_url():
    """Validar URL do vídeo"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        
        if not url:
            return jsonify({'valid': False, 'error': 'URL não fornecida'})
        
        # Validação básica por padrão de URL
        patterns = {
            'Instagram': r'instagram\.com',
            'Facebook': r'(facebook\.com|fb\.watch)',
            'TikTok': r'tiktok\.com',
            'X/Twitter': r'(twitter\.com|x\.com)'
        }
        
        pattern = patterns.get(platform, '')
        if pattern and re.search(pattern, url, re.IGNORECASE):
            return jsonify({'valid': True, 'platform': platform})
        else:
            return jsonify({'valid': False, 'error': f'URL não é válida para {platform}'})
            
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@app.route('/api/get_video_info', methods=['POST'])
def get_video_info():
    """Obter informações do vídeo usando yt-dlp"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL não fornecida'})
        
        # Configurar yt-dlp para extrair apenas informações
        ydl_opts = get_ydl_opts(platform)
        ydl_opts.update({
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # CORREÇÃO: Verificar se info não é None
            if info is None:
                return jsonify({
                    'success': False, 
                    'error': f'{platform} bloqueou a extração de informações. Tente novamente ou use outra URL.'
                })
            
            video_info = {
                'success': True,
                'title': info.get('title', 'Vídeo sem título'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'uploader': info.get('uploader', 'Desconhecido'),
                'thumbnail': info.get('thumbnail', ''),
                'platform': platform,
                'formats': [f.get('format_note', f.get('format_id', '')) for f in info.get('formats', [])[:5]],
                'url': url
            }
            
            return jsonify(video_info)
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro ao obter informações: {str(e)}'})

@app.route('/download', methods=['POST'])
def download_video():
    """Download do vídeo usando yt-dlp"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL não fornecida'})
        
        # Gerar ID único para o download
        download_id = str(uuid.uuid4())
        
        # Configurar diretório de download
        download_path = os.path.join(DOWNLOAD_DIR, download_id)
        os.makedirs(download_path, exist_ok=True)
        
        # Configurar yt-dlp
        ydl_opts = get_ydl_opts(platform, quality)
        ydl_opts.update({
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        })
        
        # Realizar download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Encontrar arquivo baixado
            files = os.listdir(download_path)
            if files:
                filename = files[0]
                filepath = os.path.join(download_path, filename)
                
                # Salvar informações do download
                download_cache[download_id] = {
                    'filename': filename,
                    'filepath': filepath,
                    'title': info.get('title', 'Video'),
                    'platform': platform,
                    'created_at': datetime.now().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'download_id': download_id,
                    'filename': filename,
                    'title': info.get('title', 'Video'),
                    'download_url': f'/file/{download_id}'
                })
            else:
                return jsonify({'success': False, 'error': 'Arquivo não encontrado após download'})
                
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro no download: {str(e)}'})

@app.route('/file/<download_id>')
def download_file(download_id):
    """Servir arquivo baixado"""
    try:
        if download_id not in download_cache:
            return jsonify({'error': 'Download não encontrado'}), 404
        
        file_info = download_cache[download_id]
        filepath = file_info['filepath']
        filename = file_info['filename']
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/privacy-policy')
def privacy_policy():
    """Política de Privacidade"""
    try:
        return render_template('privacy-policy.html')
    except:
        return "<h1>Política de Privacidade</h1><p>Em desenvolvimento</p>"

@app.route('/terms-of-service')  
def terms_of_service():
    """Termos de Serviço"""
    try:
        return render_template('terms-of-service.html')
    except:
        return "<h1>Termos de Uso</h1><p>Em desenvolvimento</p>"

@app.route('/test')
def test():
    """Endpoint de teste"""
    return jsonify({
        'message': 'Flask funcionando no Vercel!',
        'platforms': ['Instagram', 'Facebook', 'TikTok', 'X/Twitter'],
        'status': 'working',
        'yt_dlp': 'enabled'
    })

@app.route('/about')
def about():
    """Página sobre"""
    return jsonify({
        'name': 'Universal Video Downloader',
        'version': '2.0.0',
        'platforms': ['Instagram', 'Facebook', 'TikTok', 'X/Twitter'],
        'features': ['Download', 'Info', 'Multi-platform']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
