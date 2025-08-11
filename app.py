from flask import Flask, jsonify, render_template, request, send_file
import yt_dlp
import os
import tempfile
import uuid
from datetime import datetime
import re
import random

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
        'socket_timeout': 60,
        'retries': 3,
    }
    
    # Configurações específicas por plataforma
    if platform == 'Instagram':
        base_opts.update({
            'format': 'best[height<=720]/best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            'extractor_args': {
                'instagram': {
                    'api_version': 'v1',
                }
            }
        })
    elif platform == 'Facebook':
        base_opts.update({
            'format': 'best[height<=1080]/best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        })
    elif platform == 'TikTok':
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        ]
        base_opts.update({
            'format': 'best[height<=720]/best',
            'http_headers': {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.tiktok.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
            },
            'extractor_args': {
                'tiktok': {
                    'webpage_url_basename': 'video',
                    'api_hostname': 'api.tiktokv.com',
                }
            },
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'sleep_interval': 2,
            'max_sleep_interval': 5,
        })
    elif platform == 'X/Twitter':
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        ]
        base_opts.update({
            'format': 'best[height<=720]/best',
            'http_headers': {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://twitter.com/',
                'X-Requested-With': 'XMLHttpRequest',
                'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            },
            'extractor_args': {
                'twitter': {
                    'legacy_api': True,
                    'api_version': '1.1',
                }
            },
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'sleep_interval': 1,
            'max_sleep_interval': 3,
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
        print(f"[DEBUG] Download iniciado - recebendo dados...")
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        quality = data.get('quality', 'best')
        
        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] Platform: {platform}")
        print(f"[DEBUG] Quality: {quality}")
        
        if not url:
            print(f"[DEBUG] Erro: URL não fornecida")
            return jsonify({'success': False, 'error': 'URL não fornecida'})
        
        # Gerar ID único para o download
        download_id = str(uuid.uuid4())
        print(f"[DEBUG] Download ID gerado: {download_id}")
        
        # Configurar diretório de download
        download_path = os.path.join(DOWNLOAD_DIR, download_id)
        os.makedirs(download_path, exist_ok=True)
        print(f"[DEBUG] Diretório criado: {download_path}")
        
        # Configurar yt-dlp
        ydl_opts = get_ydl_opts(platform, quality)
        ydl_opts.update({
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        })
        print(f"[DEBUG] Configurações yt-dlp: {ydl_opts}")
        
        # Realizar download
        print(f"[DEBUG] Iniciando yt-dlp para {platform}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                
                if info is None:
                    print(f"[DEBUG] Erro: yt-dlp retornou None")
                    return jsonify({
                        'success': False, 
                        'error': f'{platform} bloqueou o download ou URL inválida'
                    })
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"[DEBUG] Erro específico do yt-dlp: {str(e)}")
                
                # Detectar erros específicos do Instagram
                if platform == 'Instagram' and any(keyword in error_msg for keyword in ['rate limit', 'login required', 'not available', 'dneb_']):
                    return jsonify({
                        'success': False, 
                        'error': 'Instagram bloqueou downloads em ambiente cloud. Limitações conhecidas: rate limiting agressivo e detecção de datacenter. Recomendação: use o ambiente local para Instagram.',
                        'error_type': 'instagram_cloud_blocked',
                        'suggestion': 'Para Instagram, recomendamos usar o aplicativo localmente onde funciona perfeitamente.'
                    })
                
                # Detectar erros específicos do TikTok
                if platform == 'TikTok' and any(keyword in error_msg for keyword in ['unable to extract', 'webpage video data', 'login required', 'cookies', 'blocked']):
                    return jsonify({
                        'success': False, 
                        'error': 'TikTok bloqueou downloads. Limitações conhecidas: necessidade de cookies/autenticação e detecção anti-bot. TikTok é muito restritivo contra downloaders.',
                        'error_type': 'tiktok_blocked',
                        'suggestion': 'TikTok requer cookies de navegador autenticado. Funciona melhor em ambiente local com sessão válida.'
                    })
                
                # Erro genérico para outras situações
                return jsonify({'success': False, 'error': f'Erro no {platform}: {str(e)}'})
            
            # Encontrar arquivo baixado
            files = os.listdir(download_path)
            print(f"[DEBUG] Arquivos no diretório: {files}")
            if files:
                filename = files[0]
                filepath = os.path.join(download_path, filename)
                print(f"[DEBUG] Arquivo encontrado: {filepath}")
                
                # CORREÇÃO: Verificar se arquivo realmente existe
                if not os.path.exists(filepath):
                    print(f"[DEBUG] Erro: Arquivo não existe: {filepath}")
                    return jsonify({'success': False, 'error': f'Arquivo não foi criado corretamente para {platform}'})
                
                # Salvar informações do download
                download_cache[download_id] = {
                    'filename': filename,
                    'filepath': filepath,
                    'title': info.get('title', 'Video'),
                    'platform': platform,
                    'created_at': datetime.now().isoformat()
                }
                
                print(f"[DEBUG] Download salvo no cache: {download_id}")
                return jsonify({
                    'success': True,
                    'download_id': download_id,
                    'filename': filename,
                    'title': info.get('title', 'Video'),
                    'download_url': f'/file/{download_id}'
                })
            else:
                print(f"[DEBUG] Erro: Nenhum arquivo encontrado no diretório")
                return jsonify({'success': False, 'error': f'Nenhum arquivo foi baixado para {platform}. Possível bloqueio ou URL inválida.'})
                
    except Exception as e:
        print(f"[DEBUG] Exception no download {platform}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erro no download {platform}: {str(e)}'})

@app.route('/download_direct', methods=['POST'])
def download_direct():
    """Download direto sem cache - ultra-simples para Twitter e Instagram"""
    try:
        print(f"[DEBUG] Download direto iniciado...")
        data = request.get_json()
        url = data.get('url', '').strip()
        platform = data.get('platform', '')
        
        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] Platform: {platform}")
        
        if not url:
            return jsonify({'success': False, 'error': 'URL não fornecida'})
        
        # Suportar Twitter, Instagram e TikTok
        if platform not in ['X/Twitter', 'Instagram', 'TikTok']:
            return jsonify({'success': False, 'error': f'Endpoint não suporta {platform}. Use X/Twitter, Instagram ou TikTok.'})
        
        # Criar diretório temporário único
        temp_dir = tempfile.mkdtemp()
        print(f"[DEBUG] Diretório temporário: {temp_dir}")
        
        # Configurações específicas por plataforma
        if platform == 'X/Twitter':
            ydl_opts = {
                'format': 'best[height<=720]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }
        elif platform == 'Instagram':
            ydl_opts = {
                'format': 'best[height<=720]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.instagram.com/',
                    'Origin': 'https://www.instagram.com',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Upgrade-Insecure-Requests': '1',
                },
                # Configurações anti-bloqueio para Instagram
                'sleep_interval': 2,  # Delay entre requests
                'max_sleep_interval': 5,
                'retries': 3,  # Tentar 3 vezes
                'fragment_retries': 3,
                'cookiefile': None,  # Instagram pode precisar de cookies no futuro
                # Bypass geográfico
                'geo_bypass': True,
                'geo_bypass_country': 'BR',
            }
        elif platform == 'TikTok':
            ydl_opts = {
                # FORÇAR H.264 em vez de HEVC para melhor compatibilidade
                'format': 'best[vcodec^=avc][height<=720]/best[height<=720]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.tiktok.com/',
                },
                # Configurações específicas para TikTok
                'sleep_interval': 1,
                'retries': 2,
                'fragment_retries': 2,
                # Bypass geográfico
                'geo_bypass': True,
                'geo_bypass_country': 'BR',
                # Forçar re-encoding se necessário para garantir H.264
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                    'preferedcodec': 'libx264',  # Forçar H.264
                }] if os.path.exists('/usr/bin/ffmpeg') or os.path.exists('/usr/local/bin/ffmpeg') else [],
            }
        
        print(f"[DEBUG] Iniciando yt-dlp para {platform}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                
                if info is None:
                    print(f"[DEBUG] Erro: yt-dlp retornou None")
                    return jsonify({'success': False, 'error': f'{platform} bloqueou o download ou URL inválida'})
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"[DEBUG] Erro específico do yt-dlp: {str(e)}")
                
                # Detectar erros específicos do Instagram
                if platform == 'Instagram' and any(keyword in error_msg for keyword in ['rate limit', 'login required', 'not available', 'dneb_']):
                    return jsonify({
                        'success': False, 
                        'error': 'Instagram bloqueou downloads em ambiente cloud. Limitações conhecidas: rate limiting agressivo e detecção de datacenter. Recomendação: use o ambiente local para Instagram.',
                        'error_type': 'instagram_cloud_blocked',
                        'suggestion': 'Para Instagram, recomendamos usar o aplicativo localmente onde funciona perfeitamente.'
                    })
                
                # Detectar erros específicos do TikTok
                if platform == 'TikTok' and any(keyword in error_msg for keyword in ['unable to extract', 'webpage video data', 'login required', 'cookies', 'blocked']):
                    return jsonify({
                        'success': False, 
                        'error': 'TikTok bloqueou downloads. Limitações conhecidas: necessidade de cookies/autenticação e detecção anti-bot. TikTok é muito restritivo contra downloaders.',
                        'error_type': 'tiktok_blocked',
                        'suggestion': 'TikTok requer cookies de navegador autenticado. Funciona melhor em ambiente local com sessão válida.'
                    })
                
                # Erro genérico para outras situações
                return jsonify({'success': False, 'error': f'Erro no {platform}: {str(e)}'})
            
            # Encontrar arquivo baixado
            files = os.listdir(temp_dir)
            print(f"[DEBUG] Arquivos baixados: {files}")
            
            if files:
                filename = files[0]
                filepath = os.path.join(temp_dir, filename)
                
                if os.path.exists(filepath):
                    print(f"[DEBUG] Enviando arquivo: {filepath}")
                    # Determinar extensão baseada na plataforma
                    if platform == 'X/Twitter':
                        download_name = f"twitter_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                    elif platform == 'Instagram':
                        download_name = f"instagram_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                    elif platform == 'TikTok':
                        download_name = f"tiktok_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                    
                    # Retornar arquivo diretamente
                    return send_file(
                        filepath, 
                        as_attachment=True, 
                        download_name=download_name
                    )
                else:
                    return jsonify({'success': False, 'error': 'Arquivo não encontrado'})
            else:
                return jsonify({'success': False, 'error': 'Nenhum arquivo foi baixado'})
                
    except Exception as e:
        print(f"[DEBUG] Erro no download direto: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erro: {str(e)}'})

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

@app.route('/status/<download_id>')
def download_status(download_id):
    """Verificar status do download"""
    try:
        if download_id not in download_cache:
            return jsonify({'status': 'not_found', 'error': 'Download não encontrado'}), 404
        
        file_info = download_cache[download_id]
        filepath = file_info['filepath']
        
        if os.path.exists(filepath):
            return jsonify({
                'status': 'completed',
                'filename': file_info['filename'],
                'title': file_info['title'],
                'platform': file_info['platform'],
                'download_url': f'/file/{download_id}'
            })
        else:
            return jsonify({'status': 'error', 'error': 'Arquivo não encontrado'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

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
