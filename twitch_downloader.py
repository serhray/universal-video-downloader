import os
import re
import yt_dlp
from pathlib import Path
import json
from datetime import datetime, timedelta


class TwitchDownloader:
    """Downloader para Twitch - VODs com busca e recorte de tempo"""
    
    def __init__(self):
        """Inicializar o downloader do Twitch"""
        self.platform = "Twitch"
        self.vods_cache = []
        
    def search_user_vods(self, username, max_vods=10):
        """
        Buscar VODs de um usuário do Twitch
        
        Args:
            username (str): Nome do usuário do Twitch
            max_vods (int): Quantidade máxima de VODs para buscar
            
        Returns:
            list: Lista de VODs encontrados
        """
        try:
            print(f"🔍 Buscando VODs do usuário: {username}")
            print(f"📊 Quantidade máxima: {max_vods}")
            
            # URL do canal do usuário
            channel_url = f"https://www.twitch.tv/{username}/videos"
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,  # Mudança: False para obter thumbnails completas
                'playlistend': max_vods,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                
            if not info or 'entries' not in info:
                print("❌ Nenhum VOD encontrado")
                return []
            
            vods = []
            for i, entry in enumerate(info['entries'][:max_vods], 1):
                if entry:
                    # Obter thumbnail do VOD - método melhorado
                    thumbnail = None
                    
                    # Primeiro, tentar thumbnail principal
                    if entry.get('thumbnail'):
                        thumbnail = entry.get('thumbnail')
                        print(f"[DEBUG] VOD {i}: Thumbnail principal encontrada: {thumbnail}")
                    
                    # Se não houver, procurar na lista de thumbnails
                    if not thumbnail and entry.get('thumbnails'):
                        thumbnails = entry.get('thumbnails', [])
                        if thumbnails:
                            # Filtrar thumbnails válidas e selecionar a melhor
                            valid_thumbnails = [
                                thumb for thumb in thumbnails 
                                if thumb.get('url') and thumb['url'].startswith('http')
                            ]
                            
                            if valid_thumbnails:
                                # Priorizar por resolução (width * height)
                                best_thumbnail = max(valid_thumbnails, key=lambda x: (
                                    x.get('width', 0) * x.get('height', 0)
                                ))
                                thumbnail = best_thumbnail.get('url')
                                print(f"[DEBUG] VOD {i}: Melhor thumbnail selecionada: {thumbnail}")
                    
                    if not thumbnail:
                        print(f"[DEBUG] VOD {i}: Nenhuma thumbnail encontrada")
                    
                    vod = {
                        'index': i,
                        'id': entry.get('id', 'N/A'),
                        'title': entry.get('title', 'VOD sem título'),
                        'url': entry.get('url', ''),
                        'duration': entry.get('duration', 0),
                        'upload_date': entry.get('upload_date', ''),
                        'view_count': entry.get('view_count', 0),
                        'uploader': username,
                        'thumbnail': thumbnail  # Usar thumbnail encontrada
                    }
                    vods.append(vod)
            
            self.vods_cache = vods
            print(f"✅ Encontrados {len(vods)} VODs")
            
            return vods
            
        except Exception as e:
            print(f"❌ Erro ao buscar VODs: {e}")
            return []
    
    def get_vod_details(self, vod_url):
        """
        Obter detalhes completos de um VOD específico
        
        Args:
            vod_url (str): URL do VOD
            
        Returns:
            dict: Informações detalhadas do VOD
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vod_url, download=False)
                
            # Processar informações específicas do VOD
            processed_info = {
                'title': info.get('title', 'Twitch VOD'),
                'uploader': info.get('uploader', 'Unknown'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', ''),
                'upload_date': info.get('upload_date', ''),
                'thumbnail': info.get('thumbnail', ''),
                'url': vod_url,
                'formats': info.get('formats', [])
            }
            
            return processed_info
            
        except Exception as e:
            print(f"Erro ao obter detalhes do VOD: {e}")
            return None
    
    def download_vod_segment(self, vod_url, output_path, start_time, end_time, custom_filename=None, progress_hook=None):
        """
        Baixar segmento específico de um VOD do Twitch
        
        Args:
            vod_url (str): URL do VOD
            output_path (str): Caminho para salvar
            start_time (str): Tempo de início (formato: HH:MM:SS ou MM:SS)
            end_time (str): Tempo de fim (formato: HH:MM:SS ou MM:SS)
            custom_filename (str): Nome personalizado do arquivo (opcional)
            progress_hook (callable): Função de callback para progresso
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            # Criar diretório se não existir
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Configurar nome do arquivo de saída
            if custom_filename:
                # Usar nome personalizado
                filename_base = custom_filename
                if not filename_base.endswith('.mp4'):
                    filename_base += '.mp4'
                output_template = os.path.join(output_path, filename_base)
            else:
                # Usar template padrão
                output_template = os.path.join(output_path, '%(uploader)s_%(title)s_%(upload_date)s.%(ext)s')
            
            # Converter tempos para segundos
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            
            if start_seconds >= end_seconds:
                print("❌ Erro: Tempo de início deve ser menor que tempo de fim")
                return False
            
            duration = end_seconds - start_seconds
            
            print(f"⏰ Recortando VOD:")
            print(f"   Início: {start_time} ({start_seconds}s)")
            print(f"   Fim: {end_time} ({end_seconds}s)")
            print(f"   Duração do segmento: {duration}s")
            
            # Configurações do yt-dlp para Twitch com recorte
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Preferir MP4
                'outtmpl': output_template,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': False,
                'embed_subs': False,
                # Usar argumentos externos para ffmpeg (mais compatível)
                'external_downloader': 'ffmpeg',
                'external_downloader_args': {
                    'ffmpeg_i': ['-ss', str(start_seconds), '-t', str(duration)]
                },
            }
            
            # Adicionar hook de progresso se fornecido
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Executar download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"🚀 Iniciando download do segmento do Twitch...")
                ydl.download([vod_url])
                
            print("✅ Download do segmento do Twitch concluído com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no download do segmento: {e}")
            return False
    
    def _time_to_seconds(self, time_str):
        """
        Converter string de tempo para segundos
        
        Args:
            time_str (str): Tempo no formato HH:MM:SS ou MM:SS
            
        Returns:
            int: Tempo em segundos
        """
        try:
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                raise ValueError("Formato de tempo inválido")
        except Exception as e:
            print(f"❌ Erro ao converter tempo '{time_str}': {e}")
            return 0
    
    def _seconds_to_time(self, seconds):
        """
        Converter segundos para string de tempo
        
        Args:
            seconds (int): Tempo em segundos
            
        Returns:
            str: Tempo no formato HH:MM:SS
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def validate_url(self, url):
        """
        Validar se a URL é do Twitch
        
        Args:
            url (str): URL para validar
            
        Returns:
            bool: True se válida, False caso contrário
        """
        twitch_patterns = [
            r'https?://(www\.)?twitch\.tv/[\w-]+/?.*',
            r'https?://(www\.)?twitch\.tv/videos/\d+/?.*',
            r'https?://(m\.)?twitch\.tv/[\w-]+/?.*',
        ]
        
        # Verificar se a URL contém twitch.tv
        if not 'twitch.tv' in url.lower():
            return False
        
        # Verificar padrões específicos
        for pattern in twitch_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
                
        return False
    
    def validate_username(self, username):
        """
        Validar nome de usuário do Twitch
        
        Args:
            username (str): Nome do usuário
            
        Returns:
            bool: True se válido, False caso contrário
        """
        # Nome de usuário do Twitch: 4-25 caracteres, letras, números e underscore
        pattern = r'^[a-zA-Z0-9_]{4,25}$'
        return bool(re.match(pattern, username))
    
    def format_vod_info(self, vod):
        """
        Formatar informações de um VOD para exibição
        
        Args:
            vod (dict): Informações do VOD
            
        Returns:
            str: String formatada com informações do VOD
        """
        title = vod.get('title', 'N/A')[:50] + '...' if len(vod.get('title', '')) > 50 else vod.get('title', 'N/A')
        duration = self._seconds_to_time(vod.get('duration', 0))
        upload_date = vod.get('upload_date', 'N/A')
        view_count = vod.get('view_count', 0)
        
        # Formatar data
        if upload_date != 'N/A' and len(upload_date) == 8:
            try:
                date_obj = datetime.strptime(upload_date, '%Y%m%d')
                upload_date = date_obj.strftime('%d/%m/%Y')
            except:
                pass
        
        return f"[{vod['index']}] {title} | {duration} | {upload_date} | {view_count:,} views"
    
    def debug_formats(self, url):
        """
        Debug: Mostrar formatos disponíveis para um VOD do Twitch
        
        Args:
            url (str): URL do VOD
        """
        try:
            print(f"\n=== DEBUG: Formatos disponíveis para {url} ===")
            
            info = self.get_vod_details(url)
            if not info:
                print("❌ Não foi possível obter informações do VOD")
                return
            
            print(f"🎮 Título: {info.get('title', 'N/A')}")
            print(f"👤 Streamer: {info.get('uploader', 'N/A')}")
            print(f"⏱️ Duração: {self._seconds_to_time(info.get('duration', 0))}")
            print(f"👀 Visualizações: {info.get('view_count', 'N/A')}")
            
            formats = info.get('formats', [])
            if formats:
                print(f"\n📊 Formatos disponíveis ({len(formats)}):")
                for fmt in formats:
                    format_id = fmt.get('format_id', 'N/A')
                    ext = fmt.get('ext', 'N/A')
                    height = fmt.get('height', 'N/A')
                    width = fmt.get('width', 'N/A')
                    filesize = fmt.get('filesize', 0)
                    vcodec = fmt.get('vcodec', 'N/A')
                    acodec = fmt.get('acodec', 'N/A')
                    
                    size_mb = f"{filesize / (1024*1024):.1f}MB" if filesize else "N/A"
                    resolution = f"{width}x{height}" if width != 'N/A' and height != 'N/A' else "N/A"
                    
                    print(f"  🎬 ID: {format_id} | {ext} | {resolution} | {size_mb}")
                    print(f"      Vídeo: {vcodec} | Áudio: {acodec}")
            else:
                print("❌ Nenhum formato encontrado")
            
        except Exception as e:
            print(f"❌ Erro no debug: {e}")
    
    def get_cached_vods(self):
        """
        Retornar VODs em cache da última busca
        
        Returns:
            list: Lista de VODs em cache
        """
        return self.vods_cache
    
    def download_video(self, url, output_path, progress_hook=None):
        """
        Baixar vídeo/clip completo da Twitch (método simples)
        
        Args:
            url (str): URL do vídeo/clip da Twitch
            output_path (str): Caminho para salvar
            progress_hook (callable): Função de callback para progresso
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            # Criar diretório se não existir
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Configurar nome do arquivo de saída
            output_template = os.path.join(output_path, '%(uploader)s_%(title)s.%(ext)s')
            
            print(f"🎮 Iniciando download da Twitch: {url}")
            
            # Configurações otimizadas do yt-dlp para Twitch
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Preferir MP4
                'outtmpl': output_template,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': False,
                'embed_subs': False,
                
                # Configurações de rede robustas para Twitch
                'socket_timeout': 60,
                'retries': 8,
                'fragment_retries': 8,
                'retry_sleep_functions': {
                    'http': lambda n: min(4 ** n, 60),
                    'fragment': lambda n: min(4 ** n, 60),
                },
                
                # Headers para evitar bloqueios
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                },
            }
            
            # Adicionar hook de progresso se fornecido
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Executar download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"🚀 Baixando vídeo completo da Twitch...")
                ydl.download([url])
                
            print("✅ Download da Twitch concluído com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no download da Twitch: {e}")
            return False
