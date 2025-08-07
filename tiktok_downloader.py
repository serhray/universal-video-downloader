import os
import re
import yt_dlp
from pathlib import Path
import json


class TikTokDownloader:
    """Downloader para TikTok - Vídeos Virais"""
    
    def __init__(self):
        """Inicializar o downloader do TikTok"""
        self.platform = "TikTok"
        
    def get_video_info(self, url):
        """
        Obter informações do vídeo do TikTok
        
        Args:
            url (str): URL do TikTok
            
        Returns:
            dict: Informações do vídeo
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            # Processar informações específicas do TikTok
            processed_info = {
                'title': info.get('title', 'TikTok Video'),
                'uploader': info.get('uploader', 'Unknown'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'description': info.get('description', ''),
                'upload_date': info.get('upload_date', ''),
                'thumbnail': info.get('thumbnail', ''),
                'url': url,
                'formats': info.get('formats', [])
            }
            
            return processed_info
            
        except Exception as e:
            print(f"Erro ao obter informações do TikTok: {e}")
            return None
    
    def download_video(self, url, output_path, progress_hook=None):
        """
        Baixar vídeo do TikTok no formato original
        
        Args:
            url (str): URL do TikTok
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
            
            # Configurações do yt-dlp para TikTok - FORMATO ORIGINAL
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
                print(f"Iniciando download do TikTok: {url}")
                print("Formato: Melhor qualidade disponível (original)")
                ydl.download([url])
                
            print("Download do TikTok concluído com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro no download do TikTok: {e}")
            return False
    
    def download_multiple_videos(self, urls, output_path, progress_hook=None):
        """
        Baixar múltiplos vídeos do TikTok no formato original
        
        Args:
            urls (list): Lista de URLs do TikTok
            output_path (str): Caminho para salvar
            progress_hook (callable): Função de callback para progresso
            
        Returns:
            dict: Resultados do download (sucessos e falhas)
        """
        results = {'success': [], 'failed': []}
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"Baixando vídeo {i}/{len(urls)}: {url}")
                success = self.download_video(url, output_path, progress_hook)
                
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
        Validar se a URL é do TikTok
        
        Args:
            url (str): URL para validar
            
        Returns:
            bool: True se válida, False caso contrário
        """
        tiktok_patterns = [
            # URLs padrão do TikTok
            r'https?://(www\.)?tiktok\.com/@[\w.-]+/video/\d+/?.*',
            r'https?://(m\.)?tiktok\.com/@[\w.-]+/video/\d+/?.*',
            
            # URLs encurtadas do TikTok
            r'https?://vm\.tiktok\.com/[\w-]+/?.*',
            
            # URLs com parâmetros
            r'https?://(www\.)?tiktok\.com/.*video.*',
            r'https?://(m\.)?tiktok\.com/.*video.*',
            
            # URLs de usuário com vídeo
            r'https?://(www\.)?tiktok\.com/@[\w.-]+.*',
            
            # URLs mais genéricas
            r'https?://.*tiktok\.com.*',
        ]
        
        # Verificar se a URL contém tiktok.com
        if not 'tiktok.com' in url.lower():
            return False
        
        # Verificar padrões específicos
        for pattern in tiktok_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        # Se chegou até aqui, tentar uma validação mais genérica
        # Qualquer URL do TikTok que contenha números (possível ID de vídeo)
        if 'tiktok.com' in url.lower() and (re.search(r'\d+', url) or '@' in url):
            return True
            
        return False
    
    def get_video_type(self, url):
        """
        Identificar o tipo de conteúdo do TikTok
        
        Args:
            url (str): URL do TikTok
            
        Returns:
            str: Tipo do conteúdo (video, user_video)
        """
        if '/video/' in url:
            return 'video'
        elif '@' in url:
            return 'user_video'
        elif 'vm.tiktok.com' in url:
            return 'short_url'
        else:
            return 'unknown'
    
    def debug_formats(self, url):
        """
        Debug: Mostrar formatos disponíveis para um vídeo do TikTok
        
        Args:
            url (str): URL do TikTok
        """
        try:
            print(f"\n=== DEBUG: Formatos disponíveis para {url} ===")
            
            info = self.get_video_info(url)
            if not info:
                print("❌ Não foi possível obter informações do vídeo")
                return
            
            print(f"🎵 Tipo: {self.get_video_type(url)}")
            print(f"👤 Autor: {info.get('uploader', 'N/A')}")
            print(f"📝 Título: {info.get('title', 'N/A')}")
            print(f"⏱️ Duração: {info.get('duration', 0)}s")
            print(f"👀 Visualizações: {info.get('view_count', 'N/A')}")
            print(f"❤️ Curtidas: {info.get('like_count', 'N/A')}")
            
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
    
    def test_url_access(self, url):
        """
        Testar se a URL do TikTok é acessível
        
        Args:
            url (str): URL do TikTok
            
        Returns:
            dict: Resultado do teste com detalhes
        """
        try:
            print(f"\n🔍 Testando acesso à URL do TikTok...")
            print(f"URL: {url}")
            
            ydl_opts = {
                'quiet': False,
                'no_warnings': False,
                'simulate': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            result = {
                'accessible': True,
                'title': info.get('title', 'N/A'),
                'duration': info.get('duration', 0),
                'formats_count': len(info.get('formats', [])),
                'message': 'URL acessível e vídeo encontrado'
            }
            
            print(f"✅ {result['message']}")
            print(f"📝 Título: {result['title']}")
            print(f"⏱️ Duração: {result['duration']}s")
            print(f"🎬 Formatos disponíveis: {result['formats_count']}")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            result = {
                'accessible': False,
                'error': error_msg,
                'message': f'URL não acessível: {error_msg}'
            }
            
            print(f"❌ {result['message']}")
            
            # Verificar tipos específicos de erro
            if 'private' in error_msg.lower():
                print("💡 Dica: O vídeo pode ser privado ou restrito")
            elif 'not found' in error_msg.lower():
                print("💡 Dica: O vídeo pode ter sido removido ou a URL está incorreta")
            elif 'age' in error_msg.lower():
                print("💡 Dica: O vídeo pode ter restrição de idade")
            else:
                print("💡 Dica: Verifique se a URL está correta e se o vídeo é público")
            
            return result
