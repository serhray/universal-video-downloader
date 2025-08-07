import os
import yt_dlp
import random
import time
from pathlib import Path

class YouTubeAntiBot:
    """Classe especializada para contornar detecção de bot do YouTube"""
    
    def __init__(self):
        # User-Agents rotativos (Desktop + Mobile)
        self.user_agents = [
            # Desktop Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Desktop Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Mobile (menos detectáveis)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        ]
        
        # Países para geo-bypass
        self.countries = ['US', 'CA', 'GB', 'AU', 'DE']
    
    def get_random_headers(self):
        """Gerar headers HTTP aleatórios e realistas"""
        user_agent = random.choice(self.user_agents)
        is_mobile = 'Mobile' in user_agent or 'iPhone' in user_agent
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice([
                'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'en-US,en;q=0.9,pt;q=0.8',
                'pt-BR,pt;q=0.9,en;q=0.8'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Headers específicos para desktop
        if not is_mobile:
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            })
        
        return headers
    
    def get_anti_bot_config(self, progress_hook=None):
        """Configuração definitiva anti-bot para YouTube"""
        return {
            # Headers dinâmicos e realistas
            'http_headers': self.get_random_headers(),
            
            # Rate limiting ultra-conservador
            'sleep_interval': random.uniform(3, 6),
            'max_sleep_interval': 10,
            'sleep_interval_requests': random.uniform(2, 4),
            'sleep_interval_subtitles': random.uniform(1, 2),
            
            # Configurações de rede robustas
            'socket_timeout': 90,
            'retries': 10,
            'fragment_retries': 10,
            'file_access_retries': 5,
            'retry_sleep_functions': {
                'http': lambda n: min(3 ** n, 60),
                'fragment': lambda n: min(3 ** n, 60),
                'file_access': lambda n: min(2 ** n, 30),
            },
            
            # Configurações YouTube específicas (CRÍTICAS)
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_client': ['android', 'web', 'ios', 'mweb'],
                    'player_skip': ['configs', 'webpage'],
                    'max_comments': [0],
                    'comment_sort': ['top'],
                }
            },
            
            # Bypass geo-blocking
            'geo_bypass': True,
            'geo_bypass_country': random.choice(self.countries),
            
            # Configurações anti-detecção avançadas
            'no_warnings': True,
            'ignoreerrors': False,
            'no_color': True,
            'prefer_insecure': False,
            'call_home': False,
            'no_check_certificate': False,
            
            # Configurações de cache e cookies
            'cachedir': False,
            'no_cache_dir': True,
            
            # Progress hook se fornecido
            'progress_hooks': [progress_hook] if progress_hook else [],
        }
    
    def download_with_anti_bot(self, url, output_path, quality="best", format_type="mp4", progress_hook=None):
        """Download com proteção anti-bot definitiva"""
        try:
            # Criar diretório
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Template de saída
            output_template = os.path.join(output_path, '%(title)s.%(ext)s')
            
            # Configuração base
            base_config = self.get_anti_bot_config(progress_hook)
            base_config['outtmpl'] = output_template
            
            # Configurar formato baseado no tipo
            if format_type in ['mp3', 'm4a']:
                # Áudio apenas
                base_config.update({
                    'format': 'bestaudio[ext=m4a]/bestaudio[acodec=aac]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format_type,
                        'preferredquality': '192',
                    }],
                })
            else:
                # Vídeo - seletores otimizados
                if quality == 'best':
                    format_selector = 'bestvideo[height<=1080]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio[acodec=aac]/bestvideo+bestaudio/best[height<=1080]/best'
                elif quality == 'worst':
                    format_selector = 'worst[height<=480]/worst'
                elif quality.endswith('p'):
                    height = quality[:-1]
                    format_selector = f'bestvideo[height<={height}]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio[acodec=aac]/best[height<={height}]/best'
                else:
                    format_selector = 'bestvideo[height<=720]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio[acodec=aac]/best[height<=720]/best'
                
                base_config.update({
                    'format': format_selector,
                    'merge_output_format': 'mp4',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }] if format_type == 'mp4' else [],
                })
            
            # Configurações críticas para evitar .mhtml
            base_config.update({
                'writesubtitles': False,
                'writeautomaticsub': False,
                'writedescription': False,
                'writeinfojson': False,
                'writethumbnail': False,
                'writewebvtt': False,
                'writedesktoplink': False,
                'writeurllink': False,
                'writeannotations': False,
                'noplaylist': True,
                'extract_flat': False,
                'skip_download': False,
            })
            
            # Delay inicial aleatório
            time.sleep(random.uniform(1, 3))
            
            # Executar download
            with yt_dlp.YoutubeDL(base_config) as ydl:
                print(f"🚀 Iniciando download YouTube com proteção anti-bot...")
                print(f"📱 User-Agent: {base_config['http_headers']['User-Agent'][:50]}...")
                print(f"🌍 País: {base_config['geo_bypass_country']}")
                print(f"⏱️ Rate limiting: {base_config['sleep_interval']:.1f}s")
                
                ydl.download([url])
                
            print("✅ Download YouTube concluído com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no download YouTube: {e}")
            return False
