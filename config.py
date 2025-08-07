import os
from pathlib import Path

class Config:
    """Configurações do aplicativo Universal Video Downloader"""
    
    # Configurações gerais
    APP_NAME = "Universal Video Downloader"
    VERSION = "1.0.0"
    
    # Diretórios
    DEFAULT_DOWNLOAD_PATH = os.path.expanduser("~/Downloads/VideoDownloader")
    CONFIG_DIR = os.path.expanduser("~/.video_downloader")
    
    # Configurações do YouTube
    YOUTUBE_CONFIG = {
        'default_quality': 'best',
        'default_format': 'mp4',
        'audio_quality': '192',
        'max_filesize': None,  # None = sem limite
        'subtitle_languages': ['pt', 'en'],
        'download_subtitles': False,
        'embed_subtitles': False,
        'write_description': False,
        'write_info_json': False,
        'write_thumbnail': False,
    }
    
    # Opções de qualidade disponíveis
    QUALITY_OPTIONS = {
        'best': 'Melhor Qualidade',
        'worst': 'Menor Qualidade',
        '2160p': '4K (2160p)',
        '1440p': '2K (1440p)', 
        '1080p': 'Full HD (1080p)',
        '720p': 'HD (720p)',
        '480p': 'SD (480p)',
        '360p': '360p',
        '240p': '240p',
        '144p': '144p'
    }
    
    # Formatos de vídeo suportados
    VIDEO_FORMATS = {
        'mp4': 'MP4 (Recomendado)',
        'webm': 'WebM',
        'mkv': 'MKV',
        'avi': 'AVI',
        'mov': 'MOV',
        'flv': 'FLV'
    }
    
    # Formatos de áudio suportados
    AUDIO_FORMATS = {
        'mp3': 'MP3 (Recomendado)',
        'm4a': 'M4A',
        'aac': 'AAC',
        'ogg': 'OGG',
        'wav': 'WAV',
        'flac': 'FLAC'
    }
    
    # Configurações da interface
    UI_CONFIG = {
        'theme': 'dark',
        'color_theme': 'blue',
        'window_size': '800x600',
        'min_window_size': '600x400',
        'font_size': 12,
        'language': 'pt'
    }
    
    # Configurações de rede
    NETWORK_CONFIG = {
        'timeout': 30,
        'retries': 3,
        'concurrent_downloads': 1,
        'rate_limit': None,  # None = sem limite
        'proxy': None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Plataformas suportadas (futuro)
    SUPPORTED_PLATFORMS = {
        'youtube': {
            'name': 'YouTube',
            'enabled': True,
            'icon': '🎥',
            'color': '#FF0000'
        },
        'twitch': {
            'name': 'Twitch',
            'enabled': False,  # Será implementado futuramente
            'icon': '🎮',
            'color': '#9146FF'
        },
        'kick': {
            'name': 'Kick',
            'enabled': False,
            'icon': '⚡',
            'color': '#53FC18'
        },
        'instagram': {
            'name': 'Instagram',
            'enabled': False,
            'icon': '📷',
            'color': '#E4405F'
        },
        'facebook': {
            'name': 'Facebook',
            'enabled': False,
            'icon': '👥',
            'color': '#1877F2'
        },
        'tiktok': {
            'name': 'TikTok',
            'enabled': False,
            'icon': '🎵',
            'color': '#000000'
        }
    }
    
    @classmethod
    def create_config_dir(cls):
        """Criar diretório de configuração se não existir"""
        Path(cls.CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.DEFAULT_DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_platform_info(cls, platform_name):
        """Obter informações de uma plataforma específica"""
        return cls.SUPPORTED_PLATFORMS.get(platform_name.lower(), {})
    
    @classmethod
    def is_platform_enabled(cls, platform_name):
        """Verificar se uma plataforma está habilitada"""
        platform_info = cls.get_platform_info(platform_name)
        return platform_info.get('enabled', False)
    
    @classmethod
    def get_enabled_platforms(cls):
        """Obter lista de plataformas habilitadas"""
        return [
            platform for platform, info in cls.SUPPORTED_PLATFORMS.items()
            if info.get('enabled', False)
        ]
