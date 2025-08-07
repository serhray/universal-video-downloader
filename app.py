from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit
import os
import threading
import tempfile
import uuid
from datetime import datetime
import json
import time

# Importar downloaders existentes
from youtube_downloader import YouTubeDownloader
from youtube_anti_bot import YouTubeAntiBot
from youtube_ultimate import YouTubeUltimate
from instagram_downloader import InstagramDownloader
from facebook_downloader import FacebookDownloader
from tiktok_downloader import TikTokDownloader
from twitch_downloader import TwitchDownloader
from youtube_vercel import YouTubeVercel  # Importar a solução Vercel para YouTube

app = Flask(__name__)

# SECRET KEY SEGURO - Usar variável de ambiente ou gerar aleatório
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

# Desabilitar cache em modo debug
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar downloaders
youtube_dl = YouTubeDownloader()
youtube_anti_bot = YouTubeAntiBot()  # Inicializar a solução anti-bot do YouTube
youtube_ultimate = YouTubeUltimate()  # Inicializar a solução extrema do YouTube
youtube_vercel = YouTubeVercel()  # Inicializar a solução Vercel para YouTube
instagram_dl = InstagramDownloader()
facebook_dl = FacebookDownloader()
tiktok_dl = TikTokDownloader()
twitch_dl = TwitchDownloader()

# Armazenar sessões de download ativas
active_downloads = {}

@app.route('/')
def index():
    """Página principal"""
    # Timestamp para cache busting
    timestamp = str(int(time.time()))
    return render_template('index.html', cache_bust=timestamp)

@app.route('/privacy-policy')
def privacy_policy():
    """Página de Política de Privacidade"""
    current_date = datetime.now().strftime("%d de %B de %Y")
    return render_template('privacy-policy.html', current_date=current_date)

@app.route('/terms-of-service')
def terms_of_service():
    """Página de Termos de Uso"""
    current_date = datetime.now().strftime("%d de %B de %Y")
    return render_template('terms-of-service.html', current_date=current_date)

@app.route('/api/validate_url', methods=['POST'])
def validate_url():
    """Validar URL de qualquer plataforma"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        
        if not url:
            return jsonify({'valid': False, 'message': 'URL não fornecida'})
        
        # Selecionar downloader baseado na plataforma
        downloader_map = {
            'YouTube': youtube_dl,
            'Instagram': instagram_dl,
            'Facebook': facebook_dl,
            'TikTok': tiktok_dl,
            'Twitch': twitch_dl
        }
        
        downloader = downloader_map.get(platform)
        if not downloader:
            return jsonify({'valid': False, 'message': 'Plataforma não suportada'})
        
        # Validar URL
        is_valid = downloader.validate_url(url)
        
        if is_valid:
            return jsonify({
                'valid': True, 
                'message': f'URL do {platform} válida',
                'platform': platform
            })
        else:
            return jsonify({
                'valid': False, 
                'message': f'URL inválida para {platform}'
            })
            
    except Exception as e:
        return jsonify({'valid': False, 'message': f'Erro na validação: {str(e)}'})

@app.route('/api/get_video_info', methods=['POST'])
def get_video_info():
    """Obter informações do vídeo"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        
        downloader_map = {
            'YouTube': youtube_dl,
            'Instagram': instagram_dl,
            'Facebook': facebook_dl,
            'TikTok': tiktok_dl,
            'Twitch': twitch_dl
        }
        
        downloader = downloader_map.get(platform)
        if not downloader:
            return jsonify({'success': False, 'message': 'Plataforma não suportada'})
        
        # Obter informações
        info = downloader.get_video_info(url)
        
        if info:
            # Formatar informações baseado na plataforma
            formatted_info = {
                'title': info.get('title', 'N/A'),
                'uploader': info.get('uploader', 'N/A'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'platform': platform,
                'thumbnail': info.get('thumbnail', None)  # Adicionar thumbnail
            }
            
            # Adicionar informações específicas por plataforma
            if platform == 'Instagram':
                post_type = instagram_dl.get_post_type(url)
                formatted_info['post_type'] = post_type
                
                # Verificar se é carrossel
                entries = info.get('entries', [])
                if entries:
                    formatted_info['carousel_count'] = len(entries)
                    
            elif platform == 'TikTok':
                video_type = tiktok_dl.get_video_type(url)
                formatted_info['video_type'] = video_type
                formatted_info['like_count'] = info.get('like_count', 0)
                
            elif platform == 'Facebook':
                video_type = facebook_dl.get_video_type(url)
                formatted_info['video_type'] = video_type
            
            return jsonify({'success': True, 'info': formatted_info})
        else:
            return jsonify({'success': False, 'message': 'Não foi possível obter informações do vídeo'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter informações: {str(e)}'})

@app.route('/api/download', methods=['POST'])
def download_video():
    """Iniciar download de vídeo"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        quality = data.get('quality', 'best')
        format_type = data.get('format', 'mp4')
        
        # Gerar ID único para este download
        download_id = str(uuid.uuid4())
        session_id = request.sid if hasattr(request, 'sid') else 'web'
        
        # Criar diretório temporário para este download
        temp_dir = tempfile.mkdtemp()
        
        # Armazenar informações do download
        active_downloads[download_id] = {
            'platform': platform,
            'url': url,
            'temp_dir': temp_dir,
            'status': 'starting',
            'progress': 0,
            'session_id': session_id
        }
        
        def progress_callback(d):
            """Callback para atualizar progresso via WebSocket"""
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    active_downloads[download_id]['progress'] = progress
                    socketio.emit('download_progress', {
                        'download_id': download_id,
                        'progress': progress,
                        'status': 'downloading'
                    })
                elif '_percent_str' in d:
                    # Extrair porcentagem do string
                    percent_str = d['_percent_str'].strip().replace('%', '')
                    try:
                        progress = float(percent_str)
                        active_downloads[download_id]['progress'] = progress
                        socketio.emit('download_progress', {
                            'download_id': download_id,
                            'progress': progress,
                            'status': 'downloading'
                        })
                    except:
                        pass
            elif d['status'] == 'finished':
                active_downloads[download_id]['status'] = 'completed'
                socketio.emit('download_progress', {
                    'download_id': download_id,
                    'progress': 100,
                    'status': 'completed'
                })
        
        def download_thread():
            try:
                downloader_map = {
                    'YouTube': youtube_vercel,  # Usar a solução Vercel para YouTube
                    'Instagram': instagram_dl,
                    'Facebook': facebook_dl,
                    'TikTok': tiktok_dl,
                    'Twitch': twitch_dl
                }
                
                downloader = downloader_map.get(platform)
                if not downloader:
                    active_downloads[download_id]['status'] = 'error'
                    socketio.emit('download_error', {
                        'download_id': download_id,
                        'message': 'Plataforma não suportada'
                    })
                    return
                
                # Executar download baseado na plataforma
                if platform == 'YouTube':
                    # USAR SOLUÇÃO ESPECÍFICA PARA VERCEL - Detecta ambiente automaticamente
                    success = youtube_vercel.download_video_vercel(url, temp_dir, quality, format_type, progress_callback)
                else:
                    # Para outras plataformas, usar método padrão
                    if platform == 'Instagram':
                        success = downloader.download_post(url, temp_dir, progress_callback)
                    elif platform == 'Facebook':
                        success = downloader.download_video(url, temp_dir, progress_callback)
                    elif platform == 'TikTok':
                        success = downloader.download_video(url, temp_dir, progress_callback)
                    else:
                        success = False
                
                if success:
                    active_downloads[download_id]['status'] = 'completed'
                    socketio.emit('download_complete', {
                        'download_id': download_id,
                        'message': 'Download concluído com sucesso!'
                    })
                else:
                    active_downloads[download_id]['status'] = 'error'
                    socketio.emit('download_error', {
                        'download_id': download_id,
                        'message': 'Falha no download'
                    })
                    
            except Exception as e:
                active_downloads[download_id]['status'] = 'error'
                socketio.emit('download_error', {
                    'download_id': download_id,
                    'message': f'Erro no download: {str(e)}'
                })
        
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
        return jsonify({'success': False, 'message': f'Erro ao iniciar download: {str(e)}'})

@app.route('/api/download_file/<download_id>')
def download_file(download_id):
    """Baixar arquivo após conclusão"""
    try:
        if download_id not in active_downloads:
            return jsonify({'error': 'Download não encontrado'}), 404
        
        download_info = active_downloads[download_id]
        
        if download_info['status'] != 'completed':
            return jsonify({'error': 'Download não concluído'}), 400
        
        temp_dir = download_info['temp_dir']
        
        # Encontrar arquivo baixado
        files = []
        for root, dirs, filenames in os.walk(temp_dir):
            for filename in filenames:
                if not filename.startswith('.'):  # Ignorar arquivos ocultos
                    files.append(os.path.join(root, filename))
        
        if not files:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Pegar o primeiro arquivo (ou o maior se houver múltiplos)
        file_path = max(files, key=os.path.getsize) if len(files) > 1 else files[0]
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar arquivo: {str(e)}'}), 500

# Rotas específicas do Twitch
@app.route('/api/twitch/search_vods', methods=['POST'])
def search_twitch_vods():
    """Buscar VODs do Twitch por usuário"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        max_vods = data.get('max_vods', 10)
        
        if not username:
            return jsonify({'success': False, 'message': 'Nome de usuário não fornecido'})
        
        if not twitch_dl.validate_username(username):
            return jsonify({'success': False, 'message': 'Nome de usuário inválido'})
        
        # Buscar VODs
        vods = twitch_dl.search_user_vods(username, max_vods)
        
        if vods:
            # Formatar VODs para o frontend
            formatted_vods = []
            for i, vod in enumerate(vods):
                formatted_vods.append({
                    'index': i + 1,
                    'title': vod.get('title', 'N/A'),
                    'duration': vod.get('duration', 'N/A'),
                    'upload_date': vod.get('upload_date', 'N/A'),
                    'view_count': vod.get('view_count', 0),
                    'url': vod.get('url', ''),
                    'id': vod.get('id', ''),
                    'thumbnail': vod.get('thumbnail', None)  # Incluir thumbnail
                })
            
            return jsonify({
                'success': True, 
                'vods': formatted_vods,
                'count': len(formatted_vods)
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Nenhum VOD encontrado para {username}'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro na busca: {str(e)}'})

@app.route('/api/twitch/download_segment', methods=['POST'])
def download_twitch_segment():
    """Baixar segmento de VOD do Twitch"""
    try:
        data = request.get_json()
        vod_url = data.get('vod_url', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        custom_name = data.get('custom_name', None)
        
        if not all([vod_url, start_time, end_time]):
            return jsonify({'success': False, 'message': 'Parâmetros obrigatórios faltando'})
        
        # Gerar ID único para este download
        download_id = str(uuid.uuid4())
        temp_dir = tempfile.mkdtemp()
        
        active_downloads[download_id] = {
            'platform': 'Twitch',
            'url': vod_url,
            'temp_dir': temp_dir,
            'status': 'starting',
            'progress': 0
        }
        
        def progress_callback(d):
            if d['status'] == 'downloading':
                # Atualizar progresso via WebSocket
                socketio.emit('download_progress', {
                    'download_id': download_id,
                    'progress': 50,  # Progresso estimado para segmentos
                    'status': 'downloading'
                })
        
        def download_thread():
            try:
                success = twitch_dl.download_vod_segment(
                    vod_url, temp_dir, start_time, end_time, custom_name, progress_callback
                )
                
                if success:
                    active_downloads[download_id]['status'] = 'completed'
                    socketio.emit('download_complete', {
                        'download_id': download_id,
                        'message': 'Segmento do VOD baixado com sucesso!'
                    })
                else:
                    active_downloads[download_id]['status'] = 'error'
                    socketio.emit('download_error', {
                        'download_id': download_id,
                        'message': 'Falha no download do segmento'
                    })
                    
            except Exception as e:
                active_downloads[download_id]['status'] = 'error'
                socketio.emit('download_error', {
                    'download_id': download_id,
                    'message': f'Erro no download: {str(e)}'
                })
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'Download do segmento iniciado'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao iniciar download: {str(e)}'})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f'Cliente conectado: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Cliente desconectado: {request.sid}')

if __name__ == '__main__':
    # Criar diretório de templates se não existir
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Iniciando Universal Video Downloader Web App...")
    print("📱 Acesse: http://localhost:5000")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
