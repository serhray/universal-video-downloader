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
        'status': 'running',
        'environment': 'vercel' if is_vercel else 'local'
    }

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Universal Video Downloader',
        'platforms': ['Instagram', 'Facebook', 'TikTok', 'X/Twitter'],
        'version': '1.0.0',
        'environment': 'vercel' if is_vercel else 'local'
    })

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'message': 'URL não fornecida'}), 400
        
        # Detectar plataforma pela URL
        platform = detect_platform(url)
        if not platform:
            return jsonify({'success': False, 'message': 'Plataforma não suportada'}), 400
        
        print(f"🎯 Download {platform}: {url}")
        
        # Gerar ID único
        download_id = str(uuid.uuid4())
        
        # Inicializar status
        downloads_cache[download_id] = {
            'status': 'processing',
            'platform': platform,
            'url': url,
            'progress': 0
        }
        
        # Iniciar download em thread
        thread = threading.Thread(target=process_download, args=(download_id, url, platform))
        thread.daemon = True
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
    return render_template('privacy-policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms-of-service.html')

# Endpoints para compatibilidade com frontend existente
@app.route('/api/validate_url', methods=['POST'])
def validate_url():
    """Validar URL e detectar plataforma"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'valid': False, 'message': 'URL não fornecida'})
        
        platform = detect_platform(url)
        if not platform:
            return jsonify({'valid': False, 'message': 'Plataforma não suportada'})
        
        return jsonify({
            'valid': True,
            'platform': platform,
            'message': f'URL {platform} válida'
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)})

@app.route('/api/get_video_info', methods=['POST'])
def get_video_info():
    """Obter informações do vídeo sem baixar"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'message': 'URL não fornecida'})
        
        platform = detect_platform(url)
        if not platform:
            return jsonify({'success': False, 'message': 'Plataforma não suportada'})
        
        # Configurações básicas do yt-dlp para extrair info
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'success': True,
                'info': {
                    'title': info.get('title', 'Título não disponível'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Desconhecido'),
                    'platform': platform,
                    'formats_available': len(info.get('formats', [])),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'post_type': info.get('post_type', ''),
                    'carousel_count': info.get('carousel_count', 0)
                }
            })
            
    except Exception as e:
        print(f"❌ Erro ao obter info: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

def detect_platform(url):
    """Detectar plataforma pela URL"""
    url = url.lower()
    if 'tiktok.com' in url:
        return 'TikTok'
    elif 'instagram.com' in url:
        return 'Instagram'
    elif 'facebook.com' in url or 'fb.watch' in url:
        return 'Facebook'
    elif 'twitter.com' in url or 'x.com' in url:
        return 'X/Twitter'
    return None

def process_download(download_id, url, platform):
    """Processar download em thread separada"""
    try:
        print(f"🚀 Processando {platform}: {download_id}")
        
        # Atualizar progresso
        downloads_cache[download_id]['progress'] = 10
        downloads_cache[download_id]['status'] = 'downloading'
        
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        # Configurações do yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',
            'noplaylist': True,
        }
        
        # Configurações específicas por plataforma
        if platform == 'TikTok':
            ydl_opts.update({
                'format': 'best[ext=mp4]/best',
                'cookiesfrombrowser': ('opera', None, None, None),  # Usar cookies do Opera
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'https://www.tiktok.com/'
                },
                'extractor_args': {
                    'tiktok': {
                        'webpage_url_basename': 'video',
                        'api_hostname': 'api.tiktokv.com'
                    }
                },
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'sleep_interval': 1,
                'max_sleep_interval': 3
            })
            print(f"🔧 TikTok: Configurações com cookies do Opera aplicadas para {download_id}")
        elif platform == 'Instagram':
            ydl_opts.update({
                'format': 'best',
                'cookiefile': None  # Instagram pode precisar de cookies
            })
        elif platform == 'Facebook':
            ydl_opts.update({
                'format': 'best/mp4',  # Facebook formato específico
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'extractor_args': {
                    'facebook': {
                        'legacy_ssl': True
                    }
                }
            })
            print(f"🔧 Facebook: Configurações específicas aplicadas para {download_id}")
        elif platform == 'X/Twitter':
            ydl_opts.update({
                'format': 'best',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            })
        
        print(f"📋 yt-dlp opts para {platform}: {ydl_opts}")
        
        # Atualizar progresso
        downloads_cache[download_id]['progress'] = 50
        
        print(f"🚀 Iniciando download yt-dlp para {platform}: {url}")
        
        # Executar download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"📥 Extraindo informações para {download_id}...")
            info = ydl.extract_info(url, download=True)
            print(f"✅ Extração concluída para {download_id}")
            
            # Atualizar progresso
            downloads_cache[download_id]['progress'] = 90
            print(f"📊 Progresso atualizado para 90% - {download_id}")
            
            # Encontrar arquivo baixado
            print(f"📁 Procurando arquivos em: {temp_dir}")
            files_found = os.listdir(temp_dir)
            print(f"📂 Arquivos encontrados: {files_found}")
            
            for file in files_found:
                if os.path.isfile(os.path.join(temp_dir, file)):
                    file_path = os.path.join(temp_dir, file)
                    print(f"✅ Arquivo encontrado: {file_path}")
                    
                    # Atualizar cache
                    downloads_cache[download_id].update({
                        'status': 'completed',
                        'progress': 100,
                        'file_path': file_path,
                        'filename': file,
                        'title': info.get('title', 'video'),
                        'duration': info.get('duration'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    print(f"✅ Download concluído: {file}")
                    return
        
        # Se chegou aqui, não encontrou arquivo
        downloads_cache[download_id].update({
            'status': 'failed',
            'progress': 0,
            'error': 'Arquivo não encontrado após download'
        })
        
    except Exception as e:
        print(f"❌ Erro no download {download_id}: {str(e)}")
        downloads_cache[download_id].update({
            'status': 'failed',
            'progress': 0,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🚀 Iniciando Video Downloader...")
    print("📱 Plataformas: Instagram, Facebook, TikTok, X/Twitter")
    
    if is_vercel:
        print("🌐 VERCEL detectado")
        app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("🏠 LOCAL detectado")
        print("📱 http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
