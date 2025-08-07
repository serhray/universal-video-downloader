import os
import yt_dlp
import random
import time
from pathlib import Path

class YouTubeVercel:
    """Configuração específica para YouTube no ambiente Vercel"""
    
    def __init__(self):
        # Detectar se está no Vercel
        self.is_vercel = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None
        
        # User-Agents otimizados para Vercel
        self.vercel_user_agents = [
            # Mobile (menos detectáveis em datacenters)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            
            # Desktop com características específicas
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Países com menor detecção
        self.safe_countries = ['CA', 'AU', 'NL', 'DE']
    
    def get_vercel_config(self, progress_hook=None):
        """Configuração otimizada para Vercel"""
        
        if self.is_vercel:
            # Configuração ULTRA-CONSERVADORA para Vercel
            config = {
                # Headers minimalistas
                'http_headers': {
                    'User-Agent': random.choice(self.vercel_user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                },
                
                # Timeouts MUITO baixos para Vercel (30s limit)
                'socket_timeout': 20,
                'sleep_interval': 1,
                'max_sleep_interval': 2,
                'sleep_interval_requests': 0.5,
                
                # Tentativas mínimas para não estourar timeout
                'retries': 3,
                'fragment_retries': 2,
                'file_access_retries': 2,
                
                # Configurações YouTube MINIMALISTAS
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                        'player_client': ['android'],  # Só Android (mais estável)
                        'player_skip': ['configs', 'webpage'],
                    }
                },
                
                # Geo-bypass conservador
                'geo_bypass': True,
                'geo_bypass_country': random.choice(self.safe_countries),
                
                # Configurações anti-detecção MÍNIMAS
                'no_warnings': True,
                'ignoreerrors': False,
                'no_color': True,
                'cachedir': False,
                'no_cache_dir': True,
                
                # Progress hook
                'progress_hooks': [progress_hook] if progress_hook else [],
            }
        else:
            # Configuração normal para localhost
            config = {
                'http_headers': {
                    'User-Agent': random.choice(self.vercel_user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                },
                'socket_timeout': 60,
                'sleep_interval': 2,
                'max_sleep_interval': 5,
                'retries': 8,
                'fragment_retries': 8,
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash'],
                        'player_client': ['android', 'web'],
                    }
                },
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'no_warnings': True,
                'ignoreerrors': False,
                'progress_hooks': [progress_hook] if progress_hook else [],
            }
        
        return config
    
    def download_video_vercel(self, url, output_path, quality="best", format_type="mp4", progress_hook=None):
        """Download otimizado para Vercel"""
        
        try:
            # Criar diretório
            Path(output_path).mkdir(parents=True, exist_ok=True)
            output_template = os.path.join(output_path, '%(title)s.%(ext)s')
            
            # Configuração base
            config = self.get_vercel_config(progress_hook)
            config['outtmpl'] = output_template
            
            # Configurar formato (SIMPLES para Vercel)
            if format_type in ['mp3', 'm4a']:
                config.update({
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format_type,
                        'preferredquality': '128',  # Qualidade menor para ser mais rápido
                    }],
                })
            else:
                # Formato de vídeo SIMPLES
                if quality == 'best':
                    format_selector = 'best[height<=480]/best'  # Máximo 480p no Vercel
                elif quality == 'worst':
                    format_selector = 'worst[height<=240]/worst'
                else:
                    format_selector = 'best[height<=360]/best'  # Padrão 360p
                
                config.update({
                    'format': format_selector,
                    'merge_output_format': 'mp4',
                })
            
            # Configurações críticas
            config.update({
                'writesubtitles': False,
                'writeautomaticsub': False,
                'writedescription': False,
                'writeinfojson': False,
                'writethumbnail': False,
                'noplaylist': True,
                'extract_flat': False,
                'skip_download': False,
            })
            
            # Log da configuração
            env_type = "VERCEL" if self.is_vercel else "LOCALHOST"
            print(f"🌍 Ambiente: {env_type}")
            print(f"📱 User-Agent: {config['http_headers']['User-Agent'][:50]}...")
            print(f"⏱️ Timeout: {config['socket_timeout']}s")
            print(f"🔄 Retries: {config['retries']}")
            
            # Executar download
            with yt_dlp.YoutubeDL(config) as ydl:
                ydl.download([url])
                
            print(f"✅ Download concluído no ambiente {env_type}")
            return True
            
        except Exception as e:
            print(f"❌ Erro no download: {str(e)}")
            return False


class TwitchVercel:
    """Configuração específica para Twitch no ambiente Vercel"""
    
    def __init__(self):
        # Detectar se está no Vercel
        self.is_vercel = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None
        
        # User-Agents otimizados para Vercel
        self.vercel_user_agents = [
            # Mobile (menos detectáveis em datacenters)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            
            # Desktop com características específicas
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Países com menor detecção
        self.safe_countries = ['CA', 'AU', 'NL', 'DE']
    
    def get_vercel_config(self, progress_hook=None):
        """Configuração otimizada para Twitch no Vercel"""
        
        # Configurações mais agressivas para Vercel
        if self.is_vercel:
            timeout = 30  # Timeout menor para Vercel
            retries = 5   # Menos retries no Vercel
            user_agent = random.choice(self.vercel_user_agents)
            country = random.choice(self.safe_countries)
        else:
            timeout = 60  # Timeout maior para localhost
            retries = 8   # Mais retries no localhost
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            country = 'US'
        
        config = {
            'format': 'best[ext=mp4]/best',  # Preferir MP4
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'no_warnings': False,
            'embed_subs': False,
            
            # Configurações de rede otimizadas
            'socket_timeout': timeout,
            'retries': retries,
            'fragment_retries': retries,
            'retry_sleep_functions': {
                'http': lambda n: min(2 ** n, 30),
                'fragment': lambda n: min(2 ** n, 30),
            },
            
            # Headers otimizados para Twitch
            'http_headers': {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
            },
            
            # Geo-bypass para Twitch
            'geo_bypass': True,
            'geo_bypass_country': country,
        }
        
        # Adicionar hook de progresso se fornecido
        if progress_hook:
            config['progress_hooks'] = [progress_hook]
        
        return config
    
    def download_video(self, url, output_path, progress_hook=None):
        """
        Método principal para download de vídeos da Twitch no Vercel
        Compatível com a interface esperada pelo app.py
        """
        try:
            print(f"🎮 TwitchVercel.download_video() chamado")
            print(f"🔍 URL: {url}")
            print(f"📁 Output: {output_path}")
            
            # Detectar ambiente
            env_type = "VERCEL" if self.is_vercel else "LOCAL"
            print(f"🔍 DEBUG EXTREMO - Ambiente detectado: {env_type}")
            
            # Obter configuração otimizada
            config = self.get_vercel_config(progress_hook)
            
            # Configurar diretório de saída
            config['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
            
            # Log COMPLETO da configuração
            print(f"🎮 Twitch Download - Ambiente: {env_type}")
            print(f"📱 User-Agent: {config['http_headers']['User-Agent'][:50]}...")
            print(f"⏱️ Timeout: {config['socket_timeout']}s")
            print(f"🔄 Retries: {config['retries']}")
            print(f"🌍 País: {config['geo_bypass_country']}")
            print(f"🔍 DEBUG - Formato: {config['format']}")
            print(f"🔍 DEBUG - Ignorar erros: {config.get('ignoreerrors', False)}")
            
            # Teste de conectividade básica
            print(f"🔍 DEBUG - Testando conectividade com Twitch...")
            import urllib.request
            try:
                urllib.request.urlopen('https://www.twitch.tv', timeout=10)
                print(f"✅ DEBUG - Conectividade com Twitch OK")
            except Exception as conn_e:
                print(f"❌ DEBUG - Erro de conectividade: {conn_e}")
            
            # Executar download com logs EXTREMOS
            print(f"🚀 INICIANDO download da Twitch no ambiente {env_type}...")
            print(f"🔍 DEBUG - Criando instância yt-dlp...")
            
            with yt_dlp.YoutubeDL(config) as ydl:
                print(f"✅ DEBUG - yt-dlp instanciado com sucesso")
                print(f"🔍 DEBUG - Iniciando extração de informações...")
                
                # Primeiro, tentar extrair informações
                try:
                    info = ydl.extract_info(url, download=False)
                    print(f"✅ DEBUG - Informações extraídas com sucesso")
                    print(f"🔍 DEBUG - Título: {info.get('title', 'N/A')}")
                    print(f"🔍 DEBUG - Duração: {info.get('duration', 'N/A')}")
                except Exception as info_e:
                    print(f"❌ DEBUG - Erro na extração de informações: {info_e}")
                    raise info_e
                
                # Agora tentar o download
                print(f"🔍 DEBUG - Iniciando download efetivo...")
                ydl.download([url])
                print(f"✅ DEBUG - Download concluído sem erros")
                print(f"✅ Download da Twitch concluído no ambiente {env_type}")
                
                return True
                
        except Exception as e:
            print(f"❌ TwitchVercel.download_video() ERRO: {str(e)}")
            import traceback
            print(f"🔍 DEBUG - Traceback completo:")
            traceback.print_exc()
            return False

    def download_video_vercel(self, url, output_path, progress_hook=None):
        """Download otimizado para Twitch no Vercel"""
        
        try:
            # Debug EXTREMO: Log detalhado do ambiente
            env_type = "VERCEL" if self.is_vercel else "LOCALHOST"
            print(f"🔍 DEBUG EXTREMO - Ambiente detectado: {env_type}")
            print(f"🔍 DEBUG - VERCEL env var: {os.environ.get('VERCEL', 'NOT_SET')}")
            print(f"🔍 DEBUG - VERCEL_ENV env var: {os.environ.get('VERCEL_ENV', 'NOT_SET')}")
            print(f"🔍 DEBUG - NODE_ENV env var: {os.environ.get('NODE_ENV', 'NOT_SET')}")
            print(f"🔍 DEBUG - URL da Twitch: {url}")
            print(f"🔍 DEBUG - Output path: {output_path}")
            
            # Verificar se URL é válida
            if not url or not url.startswith('https://'):
                raise ValueError(f"URL inválida: {url}")
            
            # Criar diretório com debug
            print(f"🔍 DEBUG - Criando diretório: {output_path}")
            Path(output_path).mkdir(parents=True, exist_ok=True)
            output_template = os.path.join(output_path, '%(uploader)s_%(title)s.%(ext)s')
            print(f"🔍 DEBUG - Template de saída: {output_template}")
            
            # Configuração base com debug
            print(f"🔍 DEBUG - Obtendo configuração para ambiente: {env_type}")
            config = self.get_vercel_config(progress_hook)
            config['outtmpl'] = output_template
            
            # Log COMPLETO da configuração
            print(f"🎮 Twitch Download - Ambiente: {env_type}")
            print(f"📱 User-Agent: {config['http_headers']['User-Agent'][:50]}...")
            print(f"⏱️ Timeout: {config['socket_timeout']}s")
            print(f"🔄 Retries: {config['retries']}")
            print(f"🌍 País: {config['geo_bypass_country']}")
            print(f"🔍 DEBUG - Formato: {config['format']}")
            print(f"🔍 DEBUG - Ignorar erros: {config.get('ignoreerrors', False)}")
            
            # Teste de conectividade básica
            print(f"🔍 DEBUG - Testando conectividade com Twitch...")
            import urllib.request
            try:
                urllib.request.urlopen('https://www.twitch.tv', timeout=10)
                print(f"✅ DEBUG - Conectividade com Twitch OK")
            except Exception as conn_e:
                print(f"❌ DEBUG - Erro de conectividade: {conn_e}")
            
            # Executar download com logs EXTREMOS
            print(f"🚀 INICIANDO download da Twitch no ambiente {env_type}...")
            print(f"🔍 DEBUG - Criando instância yt-dlp...")
            
            with yt_dlp.YoutubeDL(config) as ydl:
                print(f"✅ DEBUG - yt-dlp instanciado com sucesso")
                print(f"🔍 DEBUG - Iniciando extração de informações...")
                
                # Primeiro, tentar extrair informações
                try:
                    info = ydl.extract_info(url, download=False)
                    print(f"✅ DEBUG - Informações extraídas com sucesso")
                    print(f"🔍 DEBUG - Título: {info.get('title', 'N/A')}")
                    print(f"🔍 DEBUG - Duração: {info.get('duration', 'N/A')}")
                except Exception as info_e:
                    print(f"❌ DEBUG - Erro na extração de informações: {info_e}")
                    raise info_e
                
                # Agora tentar o download
                print(f"🔍 DEBUG - Iniciando download efetivo...")
                ydl.download([url])
                print(f"✅ DEBUG - Download concluído sem erros")
                print(f"✅ Download da Twitch concluído no ambiente {env_type}")
                
                return True
                
        except Exception as e:
            print(f"❌ ERRO DETALHADO no download da Twitch: {str(e)}")
            print(f"🔍 DEBUG - Tipo do erro: {type(e).__name__}")
            print(f"🔍 DEBUG - Argumentos do erro: {e.args}")
            
            # Traceback completo
            import traceback
            print(f"🔍 DEBUG - Traceback completo:")
            traceback.print_exc()
            
            # Informações do sistema
            import sys, platform
            print(f"🔍 DEBUG - Python version: {sys.version}")
            print(f"🔍 DEBUG - Platform: {platform.platform()}")
            print(f"🔍 DEBUG - Working directory: {os.getcwd()}")
            
            return False
