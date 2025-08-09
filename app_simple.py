from flask import Flask, render_template, request, jsonify, send_file, session
import os
import threading
import tempfile
import uuid
from datetime import datetime
import json
import time

# Importar todos os downloaders originais
from youtube_downloader import YouTubeDownloader
from instagram_downloader import InstagramDownloader
from facebook_downloader import FacebookDownloader
from tiktok_downloader import TikTokDownloader
from twitch_downloader import TwitchDownloader

app = Flask(__name__)

# SECRET KEY SEGURO - Usar variável de ambiente ou gerar aleatório
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

# DETECÇÃO DE AMBIENTE: Vercel ou Local
is_vercel = (
    os.environ.get('VERCEL') == '1' or 
    os.environ.get('VERCEL_ENV') is not None or
    os.environ.get('VERCEL_URL') is not None or
    'vercel' in os.environ.get('HOSTNAME', '').lower()
)

# Cache para downloads em progresso
downloads_cache = {}

# Inicializar downloaders
youtube_downloader = YouTubeDownloader()
instagram_downloader = InstagramDownloader()
facebook_downloader = FacebookDownloader()
tiktok_downloader = TikTokDownloader()
twitch_downloader = TwitchDownloader()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Página de Política de Privacidade"""
    return render_template('privacy-policy.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Universal Video Downloader',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': 'vercel' if is_vercel else 'local'
    })

@app.route('/download', methods=['POST'])
def download_video():
    """Endpoint HTTP para download (compatível com Vercel)"""
    try:
        data = request.get_json()
        url = data.get('url')
        platform = data.get('platform', 'youtube')
        quality = data.get('quality', '720p')
        format_type = data.get('format', 'mp4')
        
        if not url:
            return jsonify({'success': False, 'message': 'URL não fornecida'}), 400
        
        # Gerar ID único para o download
        download_id = str(uuid.uuid4())
        
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        # Selecionar downloader baseado na plataforma
        downloader_map = {
            'youtube': youtube_downloader,
            'instagram': instagram_downloader,
            'facebook': facebook_downloader,
            'tiktok': tiktok_downloader,
            'twitch': twitch_downloader
        }
        
        downloader = downloader_map.get(platform.lower())
        if not downloader:
            return jsonify({'success': False, 'message': f'Plataforma {platform} não suportada'}), 400
        
        def progress_callback(progress_info):
            """Callback para progresso do download - SEM SOCKETIO"""
            # Armazenar progresso no cache para polling HTTP
            downloads_cache[download_id + '_progress'] = progress_info
        
        def download_thread():
            """Thread para executar o download"""
            try:
                # Executar download
                result = downloader.download_video(
                    url=url,
                    output_path=temp_dir,
                    quality=quality,
                    format_type=format_type,
                    progress_hook=progress_callback
                )
                
                if result and 'file_path' in result:
                    # Armazenar informações do arquivo no cache
                    downloads_cache[download_id] = {
                        'file_path': result['file_path'],
                        'filename': result.get('filename', 'video.mp4'),
                        'timestamp': datetime.now(),
                        'status': 'completed'
                    }
                else:
                    downloads_cache[download_id] = {
                        'status': 'failed',
                        'error': 'Download falhou'
                    }
                        
            except Exception as e:
                downloads_cache[download_id] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Iniciar download em thread separada
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'Download iniciado'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao iniciar download: {str(e)}'}), 500

@app.route('/api/download_file/<download_id>')
def download_file(download_id):
    """Endpoint para servir arquivos baixados"""
    try:
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
        
    except Exception as e:
        return jsonify({'error': f'Erro ao servir arquivo: {str(e)}'}), 500

@app.route('/api/download_status/<download_id>')
def download_status(download_id):
    """Endpoint para verificar status do download"""
    if download_id not in downloads_cache:
        return jsonify({'status': 'not_found'}), 404
    
    download_info = downloads_cache[download_id]
    
    # Incluir progresso se disponível
    progress_info = downloads_cache.get(download_id + '_progress', {})
    
    return jsonify({
        'status': download_info.get('status', 'unknown'),
        'filename': download_info.get('filename'),
        'error': download_info.get('error'),
        'progress': progress_info
    })

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Iniciando Universal Video Downloader Web App (SIMPLIFIED)...")
    print("⚡ VERSÃO SEM SOCKETIO - Usando HTTP polling para progresso")
    
    if is_vercel:
        print("🌐 AMBIENTE VERCEL DETECTADO")
        print(f"📍 VERCEL_URL: {os.environ.get('VERCEL_URL', 'N/A')}")
        print(f"📍 VERCEL_ENV: {os.environ.get('VERCEL_ENV', 'N/A')}")
        app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("🏠 AMBIENTE LOCAL DETECTADO")
        print("📱 Acesse: http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
