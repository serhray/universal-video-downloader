import os
import re
import yt_dlp
from pathlib import Path
import json


class InstagramDownloader:
    """Downloader para Instagram - Posts, Reels e Stories"""
    
    def __init__(self):
        """Inicializar o downloader do Instagram"""
        self.platform = "Instagram"
        
    def get_video_info(self, url):
        """
        Obter informações do post/reel/story do Instagram
        
        Args:
            url (str): URL do Instagram
            
        Returns:
            dict: Informações do conteúdo
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            # Função para obter a melhor thumbnail
            def get_best_thumbnail(info_dict):
                """Obter a melhor thumbnail disponível"""
                
                # Primeiro, tentar thumbnail principal
                main_thumbnail = info_dict.get('thumbnail')
                if main_thumbnail and main_thumbnail.startswith('http'):
                    return main_thumbnail
                
                # Se não houver thumbnail principal, procurar na lista de thumbnails
                thumbnails = info_dict.get('thumbnails', [])
                if thumbnails:
                    # Filtrar thumbnails válidas
                    valid_thumbnails = [
                        thumb for thumb in thumbnails 
                        if thumb.get('url') and thumb['url'].startswith('http')
                    ]
                    
                    if valid_thumbnails:
                        # Priorizar por preferência e depois por resolução
                        best_thumb = max(valid_thumbnails, key=lambda x: (
                            x.get('preference', 0),
                            (x.get('width', 0) or 0) * (x.get('height', 0) or 0)
                        ))
                        return best_thumb.get('url')
                
                # Se for carrossel, tentar pegar thumbnail da primeira entrada
                entries = info_dict.get('entries', [])
                if entries:
                    for entry in entries:
                        entry_thumbnail = get_best_thumbnail(entry)
                        if entry_thumbnail:
                            return entry_thumbnail
                
                return None
            
            # Obter a melhor thumbnail
            best_thumbnail = get_best_thumbnail(info)
            
            # Processar informações específicas do Instagram
            processed_info = {
                'title': info.get('title', 'Instagram Post'),
                'uploader': info.get('uploader', 'Unknown'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'description': info.get('description', ''),
                'upload_date': info.get('upload_date', ''),
                'thumbnail': best_thumbnail,  # Usar a melhor thumbnail encontrada
                'url': url,
                'formats': info.get('formats', []),
                'entries': info.get('entries', [])  # Para carrosséis/múltiplos posts
            }
            
            # Debug: mostrar thumbnail selecionada
            print(f"[Instagram] Thumbnail selecionada: {best_thumbnail}")
            
            return processed_info
            
        except Exception as e:
            print(f"Erro ao obter informações do Instagram: {e}")
            return None
    
    def download_post(self, url, output_path, progress_hook=None):
        """
        Baixar post/reel/story do Instagram no formato original
        
        Args:
            url (str): URL do Instagram
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
            
            # Configurações do yt-dlp para Instagram - FORMATO ORIGINAL
            ydl_opts = {
                'format': 'best',  # Sempre o melhor formato disponível
                'outtmpl': output_template,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': False,
                'embed_subs': False,
            }
            
            # Adicionar hook de progresso se fornecido
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Executar download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Iniciando download do Instagram: {url}")
                print("Formato: Melhor qualidade disponível (original)")
                ydl.download([url])
                
            print("Download do Instagram concluído com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro no download do Instagram: {e}")
            return False
    
    def download_multiple_posts(self, urls, output_path, progress_hook=None):
        """
        Baixar múltiplos posts do Instagram no formato original
        
        Args:
            urls (list): Lista de URLs do Instagram
            output_path (str): Caminho para salvar
            progress_hook (callable): Função de callback para progresso
            
        Returns:
            dict: Resultados do download (sucessos e falhas)
        """
        results = {'success': [], 'failed': []}
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"Baixando post {i}/{len(urls)}: {url}")
                success = self.download_post(url, output_path, progress_hook)
                
                if success:
                    results['success'].append(url)
                else:
                    results['failed'].append(url)
                    
            except Exception as e:
                print(f"Erro ao baixar {url}: {e}")
                results['failed'].append(url)
        
        return results
    
    def validate_url(self, url):
        """
        Validar se a URL é do Instagram
        
        Args:
            url (str): URL para validar
            
        Returns:
            bool: True se válida, False caso contrário
        """
        instagram_patterns = [
            r'https?://(www\.)?instagram\.com/p/[\w-]+/?',      # Posts
            r'https?://(www\.)?instagram\.com/reel/[\w-]+/?',   # Reels
            r'https?://(www\.)?instagram\.com/stories/[\w.-]+/\d+/?',  # Stories
            r'https?://(www\.)?instagram\.com/tv/[\w-]+/?',     # IGTV
        ]
        
        return any(re.match(pattern, url) for pattern in instagram_patterns)
    
    def get_post_type(self, url):
        """
        Identificar o tipo de conteúdo do Instagram
        
        Args:
            url (str): URL do Instagram
            
        Returns:
            str: Tipo do conteúdo (post, reel, story, igtv)
        """
        if '/p/' in url:
            return 'post'
        elif '/reel/' in url:
            return 'reel'
        elif '/stories/' in url:
            return 'story'
        elif '/tv/' in url:
            return 'igtv'
        else:
            return 'unknown'
    
    def debug_formats(self, url):
        """
        Debug: Mostrar formatos disponíveis para um post do Instagram
        
        Args:
            url (str): URL do Instagram
        """
        try:
            print(f"\n=== DEBUG: Formatos disponíveis para {url} ===")
            
            info = self.get_video_info(url)
            if not info:
                print("❌ Não foi possível obter informações do post")
                return
            
            print(f"📱 Tipo: {self.get_post_type(url)}")
            print(f"👤 Autor: {info.get('uploader', 'N/A')}")
            print(f"📝 Título: {info.get('title', 'N/A')}")
            print(f"⏱️ Duração: {info.get('duration', 0)}s")
            
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
            
            # Verificar se é carrossel (múltiplas imagens/vídeos)
            entries = info.get('entries', [])
            if entries:
                print(f"\n📸 Carrossel detectado: {len(entries)} itens")
                for i, entry in enumerate(entries, 1):
                    entry_type = "Vídeo" if entry.get('duration', 0) > 0 else "Imagem"
                    print(f"  {i}. {entry_type}: {entry.get('title', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Erro no debug: {e}")
