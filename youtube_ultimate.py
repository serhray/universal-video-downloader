import os
import yt_dlp
import random
import time
from pathlib import Path

class YouTubeUltimate:
    """Solução EXTREMA para YouTube - Múltiplas estratégias de fallback"""
    
    def __init__(self):
        # User-Agents ultra-diversificados
        self.user_agents = [
            # Chrome Desktop
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Firefox Desktop
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Safari Desktop
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            
            # Mobile (menos detectáveis)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        ]
        
        # Países para geo-bypass
        self.countries = ['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'NL', 'JP']
        
        # Configurações de fallback
        self.fallback_configs = [
            # Configuração 1: Ultra-conservadora
            {
                'name': 'Ultra Conservative',
                'sleep_interval': 5,
                'max_sleep_interval': 10,
                'retries': 15,
                'player_client': ['android'],
                'skip': ['dash', 'hls'],
            },
            # Configuração 2: Mobile-first
            {
                'name': 'Mobile First',
                'sleep_interval': 3,
                'max_sleep_interval': 8,
                'retries': 12,
                'player_client': ['ios', 'android', 'mweb'],
                'skip': ['dash'],
            },
            # Configuração 3: Web-only
            {
                'name': 'Web Only',
                'sleep_interval': 4,
                'max_sleep_interval': 9,
                'retries': 10,
                'player_client': ['web'],
                'skip': ['hls'],
            },
            # Configuração 4: Minimal
            {
                'name': 'Minimal',
                'sleep_interval': 2,
                'max_sleep_interval': 6,
                'retries': 8,
                'player_client': ['android', 'web'],
                'skip': [],
            }
        ]
    
    def get_extreme_headers(self, mobile=False):
        """Headers extremamente realistas"""
        user_agent = random.choice(self.user_agents)
        is_mobile = mobile or 'Mobile' in user_agent or 'iPhone' in user_agent
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice([
                'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
                'pt-BR,pt;q=0.9,en;q=0.8,es;q=0.7'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Headers específicos por navegador
        if 'Chrome' in user_agent and not is_mobile:
            headers.update({
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            })
        elif 'Firefox' in user_agent:
            headers.update({
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            })
        
        return headers
    
    def get_fallback_config(self, config_index, progress_hook=None):
        """Configuração de fallback específica"""
        config = self.fallback_configs[config_index % len(self.fallback_configs)]
        
        return {
            # Headers dinâmicos
            'http_headers': self.get_extreme_headers(),
            
            # Rate limiting baseado na configuração
            'sleep_interval': config['sleep_interval'],
            'max_sleep_interval': config['max_sleep_interval'],
            'sleep_interval_requests': config['sleep_interval'] / 2,
            'sleep_interval_subtitles': 1,
            
            # Configurações de rede ultra-robustas
            'socket_timeout': 120,
            'retries': config['retries'],
            'fragment_retries': config['retries'],
            'file_access_retries': 8,
            'retry_sleep_functions': {
                'http': lambda n: min(5 ** n, 120),
                'fragment': lambda n: min(5 ** n, 120),
                'file_access': lambda n: min(3 ** n, 60),
            },
            
            # Configurações YouTube EXTREMAS
            'extractor_args': {
                'youtube': {
                    'skip': config['skip'],
                    'player_client': config['player_client'],
                    'player_skip': ['configs', 'webpage'],
                    'max_comments': [0],
                    'comment_sort': ['top'],
                    'innertube_host': ['youtubei.googleapis.com'],
                    'innertube_key': ['AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'],
                }
            },
            
            # Bypass geo-blocking extremo
            'geo_bypass': True,
            'geo_bypass_country': random.choice(self.countries),
            
            # Configurações anti-detecção EXTREMAS
            'no_warnings': True,
            'ignoreerrors': False,
            'no_color': True,
            'prefer_insecure': False,
            'call_home': False,
            'no_check_certificate': True,  # EXTREMO
            
            # Cache e cookies
            'cachedir': False,
            'no_cache_dir': True,
            
            # Progress hook
            'progress_hooks': [progress_hook] if progress_hook else [],
        }
    
    def download_with_extreme_fallback(self, url, output_path, quality="best", format_type="mp4", progress_hook=None):
        """Download com fallback extremo - tenta todas as configurações"""
        
        # Criar diretório
        Path(output_path).mkdir(parents=True, exist_ok=True)
        output_template = os.path.join(output_path, '%(title)s.%(ext)s')
        
        # Tentar cada configuração de fallback
        for i, fallback_config in enumerate(self.fallback_configs):
            try:
                print(f"🚀 Tentativa {i+1}/4: {fallback_config['name']}")
                
                # Configuração base
                base_config = self.get_fallback_config(i, progress_hook)
                base_config['outtmpl'] = output_template
                
                # Configurar formato
                if format_type in ['mp3', 'm4a']:
                    base_config.update({
                        'format': 'bestaudio[ext=m4a]/bestaudio[acodec=aac]/bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': format_type,
                            'preferredquality': '192',
                        }],
                    })
                else:
                    # Seletores de formato mais agressivos
                    if quality == 'best':
                        format_selector = 'bestvideo[height<=720]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio[acodec=aac]/best[height<=720]/best'
                    elif quality == 'worst':
                        format_selector = 'worst[height<=360]/worst'
                    elif quality.endswith('p'):
                        height = quality[:-1]
                        format_selector = f'bestvideo[height<={height}]+bestaudio[ext=m4a]/best[height<={height}]/best'
                    else:
                        format_selector = 'bestvideo[height<=480]+bestaudio[ext=m4a]/best[height<=480]/best'
                    
                    base_config.update({
                        'format': format_selector,
                        'merge_output_format': 'mp4',
                        'postprocessors': [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4',
                        }] if format_type == 'mp4' else [],
                    })
                
                # Configurações críticas
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
                time.sleep(random.uniform(2, 5))
                
                # Executar download
                with yt_dlp.YoutubeDL(base_config) as ydl:
                    print(f"📱 User-Agent: {base_config['http_headers']['User-Agent'][:50]}...")
                    print(f"🌍 País: {base_config['geo_bypass_country']}")
                    print(f"⏱️ Rate limiting: {base_config['sleep_interval']}s")
                    print(f"🎯 Player clients: {base_config['extractor_args']['youtube']['player_client']}")
                    
                    ydl.download([url])
                    
                print(f"✅ Sucesso com configuração: {fallback_config['name']}")
                return True
                
            except Exception as e:
                print(f"❌ Falha na tentativa {i+1}: {str(e)[:100]}...")
                if i < len(self.fallback_configs) - 1:
                    print(f"🔄 Tentando próxima configuração em 3s...")
                    time.sleep(3)
                continue
        
        print("❌ Todas as tentativas falharam")
        return False
