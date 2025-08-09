from flask import Flask, jsonify, request, send_file, render_template
import os
import tempfile
import uuid
import yt_dlp
from datetime import datetime
import threading

app = Flask(__name__)

# DETECÇÃO DE AMBIENTE: Vercel ou Local
is_vercel = (
    'VERCEL' in os.environ or 
    'VERCEL_ENV' in os.environ
)

# Cache para downloads
downloads_cache = {}

@app.route('/')
def index():
    """Página principal com interface completa"""
    return render_template('index.html', 
                         cache_bust=str(int(datetime.now().timestamp())))

@app.route('/api/info')
def api_info():
    """API info endpoint"""
    return {
        'message': 'Universal Video Downloader',
        'platforms': ['Instagram', 'Facebook', 'TikTok', 'X/Twitter'],
        'environment': 'Vercel' if is_vercel else 'Local',
        'status': 'active'
    }

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Universal Video Downloader',
        'environment': 'Vercel' if is_vercel else 'Local',
        'platforms': ['Instagram', 'Facebook', 'TikTok', 'X/Twitter']
    })

def download_video_yt_dlp(url, platform, download_id):
    """Download usando yt-dlp para todas as plataformas"""
    try:
        print(f"🚀 Iniciando download {platform}: {url}")
        
        # Configurações base do yt-dlp
        temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',
            'noplaylist': True,
            'extractaudio': False,
            'audioformat': 'mp3',
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        # Configurações específicas por plataforma
        if platform.lower() == 'instagram':
            ydl_opts.update({
                'format': 'best',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            })
        elif platform.lower() == 'facebook':
            ydl_opts.update({
                'format': 'best',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            })
        elif platform.lower() == 'tiktok':
            ydl_opts.update({
                'format': 'best',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            })
        elif platform.lower() in ['x/twitter', 'twitter', 'x']:
            ydl_opts.update({
                'format': 'best',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            })
        
        # Atualizar status
        downloads_cache[download_id].update({
            'status': 'downloading',
            'progress': 50,
            'message': f'Baixando {platform}...'
        })
        
        # Download com yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Encontrar arquivo baixado
            for file in os.listdir(temp_dir):
                if file.endswith(('.mp4', '.webm', '.mkv', '.avi')):
                    file_path = os.path.join(temp_dir, file)
                    
                    # Atualizar cache com sucesso
                    downloads_cache[download_id].update({
                        'status': 'completed',
                        'progress': 100,
                        'message': f'Download {platform} concluído!',
                        'file_path': file_path,
                        'filename': file,
                        'title': info.get('title', 'Video'),
                        'duration': info.get('duration', 0)
                    })
                    
                    print(f"✅ Download {platform} concluído: {file}")
                    return
        
        # Se chegou aqui, não encontrou arquivo
        downloads_cache[download_id].update({
            'status': 'error',
            'message': f'Erro: arquivo não encontrado após download {platform}'
        })
        
    except Exception as e:
        print(f"❌ Erro no download {platform}: {str(e)}")
        downloads_cache[download_id].update({
            'status': 'error',
            'message': f'Erro no download {platform}: {str(e)}'
        })

@app.route('/download', methods=['POST'])
def download():
    """Endpoint HTTP para download (compatível com Vercel)"""
    try:
        data = request.get_json()
        url = data.get('url')
        platform = data.get('platform', 'Unknown')
        
        if not url:
            return jsonify({'success': False, 'message': 'URL é obrigatória'}), 400
        
        # Gerar ID único para o download
        download_id = str(uuid.uuid4())
        
        # Inicializar cache
        downloads_cache[download_id] = {
            'status': 'started',
            'progress': 0,
            'message': f'Iniciando download {platform}...',
            'url': url,
            'platform': platform
        }
        
        # Iniciar download em thread separada
        thread = threading.Thread(
            target=download_video_yt_dlp,
            args=(url, platform, download_id)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'platform': platform,
            'message': f'Download {platform} iniciado'
        })
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/status/<download_id>')
def download_status(download_id):
    if download_id not in downloads_cache:
        return jsonify({'status': 'not_found'}), 404
    
    return jsonify(downloads_cache[download_id])

@app.route('/file/<download_id>')
def download_file(download_id):
    if download_id not in downloads_cache:
        return jsonify({'error': 'Download não encontrado'}), 404
    
    download_info = downloads_cache[download_id]
    
    if download_info.get('status') != 'completed':
        return jsonify({'error': 'Download não concluído'}), 400
    
    file_path = download_info.get('file_path')
    filename = download_info.get('filename', 'video.mp4')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/api/download_file/<download_id>')
def api_download_file(download_id):
    """Endpoint compatível para download de arquivo"""
    return download_file(download_id)

# Rotas para templates adicionais
@app.route('/privacy-policy')
def privacy_policy():
    """Página de política de privacidade"""
    return render_template('privacy-policy.html')

@app.route('/terms')
def terms():
    """Página de termos de uso"""
    return render_template('terms.html')

@app.route('/about')
def about():
    """Página sobre o projeto"""
    return render_template('about.html')

if __name__ == '__main__':
    if is_vercel:
        print("🌐 VERCEL: Aplicação Flask iniciada")
        print("🎯 VERCEL: Plataformas suportadas: Instagram, Facebook, TikTok, X/Twitter")
    else:
        print("🏠 LOCAL: Iniciando servidor Flask...")
        print("🎯 LOCAL: Plataformas suportadas: Instagram, Facebook, TikTok, X/Twitter")
        print("🌐 LOCAL: Acesse http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
