import os
import yt_dlp
import random
import re
from pathlib import Path

class YouTubeDownloader:
    def __init__(self):
        self.name = "YouTube"
        # Lista de User-Agents rotativos para evitar detecção
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Mobile User-Agents (menos detectáveis)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        ]
    
    def get_video_info(self, url):
        """Obter informações detalhadas do vídeo sem baixar"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extract_flat': False,
            # Opções críticas para evitar .mhtml
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writedescription': False,
            'writeinfojson': False,
            'writethumbnail': False,
            'writewebvtt': False,
            'writedesktoplink': False,
            'writeurllink': False,
            'writeannotations': False,
            # Headers anti-bot para obter informações
            'http_headers': {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            raise Exception(f"Erro ao obter informações do vídeo: {str(e)}")
    
    def download_video(self, url, output_path, quality="best", format_type="mp4", progress_hook=None):
        """
        Baixar vídeo do YouTube - VERSÃO CORRIGIDA PARA EVITAR .mhtml
        
        Args:
            url (str): URL do vídeo
            output_path (str): Caminho de destino
            quality (str): Qualidade desejada (best, worst, 720p, etc.)
            format_type (str): Formato do arquivo (mp4, webm, mkv, mp3, m4a)
            progress_hook (callable): Função callback para progresso
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            # Criar diretório se não existir
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Configurar nome do arquivo de saída
            output_template = os.path.join(output_path, '%(title)s.%(ext)s')
            
            # CONFIGURAÇÃO ULTRA-SIMPLES E TESTADA
            if format_type in ['mp3', 'm4a']:
                # Para áudio apenas
                ydl_opts = {
                    'outtmpl': output_template,
                    'format': 'bestaudio/best',
                    'progress_hooks': [progress_hook] if progress_hook else [],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format_type,
                        'preferredquality': '192',
                    }],
                    # Opções críticas para evitar .mhtml
                    'writesubtitles': False,
                    'writeautomaticsub': False,
                    'writedescription': False,
                    'writeinfojson': False,
                    'writethumbnail': False,
                }
            else:
                # Para vídeo - SELETORES SIMPLIFICADOS E EFICAZES
                if quality == 'best':
                    # Seletor simplificado para máxima qualidade
                    format_selector = 'best[height>=720]/bestvideo+bestaudio/best'
                elif quality == 'worst':
                    format_selector = 'worst'
                elif quality.endswith('p'):
                    height = quality[:-1]
                    # Seletor específico para altura desejada
                    format_selector = f'best[height<={height}]/bestvideo[height<={height}]+bestaudio/best'
                else:
                    format_selector = 'best[height>=720]/bestvideo+bestaudio/best'
                
                ydl_opts = {
                    'outtmpl': output_template,
                    'format': format_selector,
                    'progress_hooks': [progress_hook] if progress_hook else [],
                    # ANTI-BOT AVANÇADO: Headers HTTP realistas
                    'http_headers': {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                    },
                    # ANTI-BOT AVANÇADO: Rate limiting mais agressivo
                    'sleep_interval': 2,
                    'max_sleep_interval': 5,
                    'sleep_interval_requests': 2,
                    'sleep_interval_subtitles': 1,
                    # ANTI-BOT AVANÇADO: Configurações de rede
                    'socket_timeout': 60,
                    'retries': 5,
                    'fragment_retries': 5,
                    'retry_sleep_functions': {
                        'http': lambda n: min(4 ** n, 60),
                        'fragment': lambda n: min(4 ** n, 60),
                    },
                    # ANTI-BOT AVANÇADO: Configurações YouTube específicas
                    'extractor_args': {
                        'youtube': {
                            'skip': ['dash', 'hls'],
                            'player_client': ['android', 'web'],
                            'player_skip': ['configs'],
                        }
                    },
                    # ANTI-BOT AVANÇADO: Bypass de geo-blocking
                    'geo_bypass': True,
                    'geo_bypass_country': 'US',
                    # Opções críticas para evitar .mhtml
                    'writesubtitles': False,
                    'writeautomaticsub': False,
                    'writedescription': False,
                    'writeinfojson': False,
                    'writethumbnail': False,
                    'writewebvtt': False,
                    'writedesktoplink': False,
                    'writeurllink': False,
                    'writeannotations': False,
                    # Forçar download de vídeo real
                    'noplaylist': True,
                    'extract_flat': False,
                    # Garantir formato de saída compatível
                    'merge_output_format': 'mp4',
                    # Garantir que não baixe apenas metadados
                    'skip_download': False,
                    # ANTI-BOT AVANÇADO: Configurações adicionais
                    'no_warnings': True,
                    'ignoreerrors': False,
                    'no_color': True,
                    'prefer_insecure': False,
                    # Pós-processamento para garantir áudio compatível
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }] if format_type == 'mp4' else [],
                }
            
            print(f"[YouTube] URL: {url}")
            print(f"[YouTube] Qualidade: {quality}, Formato: {format_type}")
            print(f"[YouTube] Seletor: {ydl_opts.get('format', 'N/A')}")
            print(f"[YouTube] Output: {output_template}")
            
            # Realizar download com configurações corrigidas
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return True
            
        except Exception as e:
            print(f"[YouTube] ERRO: {str(e)}")
            return False
    
    def get_available_formats(self, url):
        """Obter formatos disponíveis para o vídeo"""
        try:
            info = self.get_video_info(url)
            formats = info.get('formats', [])
            
            available_formats = []
            for fmt in formats:
                if fmt.get('vcodec') != 'none':  # Apenas formatos com vídeo
                    available_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'resolution': fmt.get('resolution', 'N/A'),
                        'height': fmt.get('height'),
                        'width': fmt.get('width'),
                        'filesize': fmt.get('filesize'),
                        'fps': fmt.get('fps'),
                        'vcodec': fmt.get('vcodec'),
                        'acodec': fmt.get('acodec'),
                    })
            
            # Ordenar por altura (qualidade)
            available_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
            return available_formats
            
        except Exception as e:
            raise Exception(f"Erro ao obter formatos: {str(e)}")
    
    def download_playlist(self, url, output_path, quality="best", format_type="mp4", progress_hook=None):
        """Baixar playlist completa do YouTube"""
        try:
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            format_selector = 'best[ext=mp4]/best'
            output_template = os.path.join(output_path, '%(playlist_index)s - %(title)s.%(ext)s')
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': output_template,
                'progress_hooks': [progress_hook] if progress_hook else [],
                'extract_flat': False,
                'noplaylist': False,  # Permitir playlists
                'merge_output_format': format_type if format_type in ['mp4', 'mkv', 'webm'] else None,
            }
            
            if format_type in ['mp3', 'm4a']:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format_type,
                        'preferredquality': '192',
                    }],
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return True
            
        except Exception as e:
            print(f"Erro durante o download da playlist: {str(e)}")
            return False
    
    def search_videos(self, query, max_results=10):
        """Buscar vídeos no YouTube"""
        try:
            search_url = f"ytsearch{max_results}:{query}"
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(search_url, download=False)
                
                videos = []
                for entry in search_results.get('entries', []):
                    videos.append({
                        'title': entry.get('title'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'duration': entry.get('duration'),
                        'uploader': entry.get('uploader'),
                        'view_count': entry.get('view_count'),
                    })
                
                return videos
                
        except Exception as e:
            raise Exception(f"Erro na busca: {str(e)}")
    
    def validate_url(self, url):
        """Validar se a URL é do YouTube"""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        
        return False
    
    def debug_formats(self, url):
        """Função de debug para ver formatos disponíveis"""
        try:
            print(f"Analisando formatos disponíveis para: {url}")
            formats = self.get_available_formats(url)
            
            print("\nFormatos disponíveis:")
            print("-" * 80)
            print(f"{'ID':<10} {'Ext':<8} {'Resolução':<12} {'Altura':<8} {'Codec':<15}")
            print("-" * 80)
            
            for fmt in formats[:15]:  # Mostrar apenas os primeiros 15
                print(f"{fmt.get('format_id', 'N/A'):<10} "
                      f"{fmt.get('ext', 'N/A'):<8} "
                      f"{fmt.get('resolution', 'N/A'):<12} "
                      f"{fmt.get('height', 'N/A'):<8} "
                      f"{fmt.get('vcodec', 'N/A'):<15}")
            
            print("-" * 80)
            
        except Exception as e:
            print(f"Erro ao analisar formatos: {e}")
    
    def debug_complete_flow(self, url, quality="720p", format_type="mp4"):
        """Debug completo do fluxo de seleção de formato"""
        print(f"\n{'='*80}")
        print(f"DEBUG COMPLETO - URL: {url}")
        print(f"Qualidade solicitada: {quality}")
        print(f"Formato solicitado: {format_type}")
        print(f"{'='*80}")
        
        try:
            # 1. Verificar qual método será usado
            print(f"\n1. DECISÃO DE MÉTODO:")
            print(f"   quality not in ['original']: {quality not in ['original']}")
            print(f"   format_type not in ['mp3', 'm4a']: {format_type not in ['mp3', 'm4a']}")
            
            will_use_smart = quality not in ['original'] and format_type not in ['mp3', 'm4a']
            print(f"   → Usará _get_smart_format_selector: {will_use_smart}")
            
            # 2. Obter formatos disponíveis
            print(f"\n2. FORMATOS DISPONÍVEIS:")
            info = self.get_video_info(url)
            formats = info.get('formats', [])
            print(f"   Total de formatos: {len(formats)}")
            
            # Mostrar formatos muxed (com vídeo + áudio)
            muxed_formats = []
            video_only_formats = []
            
            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('height'):
                    muxed_formats.append(fmt)
                elif fmt.get('vcodec') != 'none' and fmt.get('height'):
                    video_only_formats.append(fmt)
            
            print(f"   Formatos MUXED (vídeo+áudio): {len(muxed_formats)}")
            for fmt in muxed_formats[:10]:
                print(f"     ID: {fmt.get('format_id'):<6} | {fmt.get('width')}x{fmt.get('height')} | {fmt.get('ext')} | {fmt.get('vcodec')}")
            
            print(f"   Formatos VÍDEO APENAS: {len(video_only_formats)}")
            for fmt in video_only_formats[:10]:
                print(f"     ID: {fmt.get('format_id'):<6} | {fmt.get('width')}x{fmt.get('height')} | {fmt.get('ext')} | {fmt.get('vcodec')}")
            
            # 3. Testar seleção inteligente
            if will_use_smart:
                print(f"\n3. TESTE DE SELEÇÃO INTELIGENTE:")
                target_height = int(quality[:-1]) if quality.endswith('p') else None
                print(f"   Altura alvo: {target_height}")
                
                # Filtrar muxed adequados
                suitable_muxed = [fmt for fmt in muxed_formats 
                                if fmt.get('height') <= target_height and fmt.get('ext') == format_type]
                print(f"   Muxed adequados para {quality} em {format_type}: {len(suitable_muxed)}")
                
                if suitable_muxed:
                    suitable_muxed.sort(key=lambda x: x.get('height', 0), reverse=True)
                    best = suitable_muxed[0]
                    print(f"   → MELHOR MUXED: ID {best.get('format_id')} - {best.get('height')}p")
                else:
                    print(f"   → Nenhum muxed adequado encontrado")
                    
                    # Testar vídeo apenas
                    suitable_video = [fmt for fmt in video_only_formats 
                                    if fmt.get('height') <= target_height and fmt.get('ext') == format_type]
                    print(f"   Vídeo adequados para {quality} em {format_type}: {len(suitable_video)}")
                    
                    if suitable_video:
                        suitable_video.sort(key=lambda x: x.get('height', 0), reverse=True)
                        best = suitable_video[0]
                        print(f"   → MELHOR VÍDEO: ID {best.get('format_id')} - {best.get('height')}p")
                
                # Executar seleção real
                format_selector = 'best[ext=mp4]/best'
                print(f"   → SELETOR RETORNADO: {format_selector}")
            
            else:
                print(f"\n3. TESTE DE SELEÇÃO PADRÃO:")
                format_selector = 'best[ext=mp4]/best'
                print(f"   → SELETOR RETORNADO: {format_selector}")
            
            # 4. Simular o que o yt-dlp faria
            print(f"\n4. SIMULAÇÃO YT-DLP:")
            print(f"   Formato que será usado: {format_selector}")
            
            # Testar qual formato o yt-dlp realmente selecionaria
            test_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': format_selector,
                'simulate': True,
                'listformats': False,
            }
            
            with yt_dlp.YoutubeDL(test_opts) as ydl:
                try:
                    test_info = ydl.extract_info(url, download=False)
                    selected_format = test_info.get('format_id', 'N/A')
                    selected_height = test_info.get('height', 'N/A')
                    selected_ext = test_info.get('ext', 'N/A')
                    print(f"   → YT-DLP SELECIONARIA: ID {selected_format} - {selected_height}p - {selected_ext}")
                except Exception as e:
                    print(f"   → ERRO NA SIMULAÇÃO: {e}")
            
            print(f"\n{'='*80}")
            
        except Exception as e:
            print(f"ERRO NO DEBUG: {e}")
