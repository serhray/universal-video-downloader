import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
from youtube_downloader import YouTubeDownloader
from instagram_downloader import InstagramDownloader
from facebook_downloader import FacebookDownloader
from tiktok_downloader import TikTokDownloader
from twitch_downloader import TwitchDownloader
from twitch_vod_interface import TwitchVODInterface
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VideoDownloaderApp:
    def __init__(self):
        # Configurar tema do CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("Download Universal - Multi-Platform Video Downloader")
        self.root.geometry("800x700")
        self.root.minsize(600, 400)
        
        # Inicializar downloaders
        self.youtube_downloader = YouTubeDownloader()
        self.instagram_downloader = InstagramDownloader()
        self.facebook_downloader = FacebookDownloader()
        self.tiktok_downloader = TikTokDownloader()
        self.twitch_downloader = TwitchDownloader()
        
        # Interface específica do Twitch
        self.twitch_interface = TwitchVODInterface(self)
        self.twitch_ui_frame = None
        
        # Estado da interface
        self.current_platform = None
        self.is_twitch_mode = False
        
        # Variáveis
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.url_var = tk.StringVar()
        self.platform_var = tk.StringVar(value="YouTube")
        self.quality_var = tk.StringVar(value="720p")
        self.format_var = tk.StringVar(value="mp4")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Universal Video Downloader", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Frame principal de conteúdo
        self.main_content_frame = ctk.CTkFrame(main_frame)
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Criar interface padrão
        self.create_standard_interface()
        
        # Criar interface do Twitch (oculta inicialmente)
        self.twitch_ui_frame = self.twitch_interface.create_twitch_interface(self.main_content_frame)
        self.twitch_interface.hide()
        
        # Botões de ação
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.download_btn = ctk.CTkButton(
            button_frame,
            text="Baixar Vídeo",
            command=self.download_video,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.download_btn.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        info_btn = ctk.CTkButton(
            button_frame,
            text="Info do Vídeo",
            command=self.get_video_info,
            height=40,
            width=120
        )
        info_btn.pack(side="right", padx=10, pady=10)
        
        debug_btn = ctk.CTkButton(
            button_frame,
            text="Debug Formatos",
            command=self.debug_formats,
            height=40,
            width=120
        )
        debug_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Barra de progresso
        self.progress_frame = ctk.CTkFrame(main_frame)
        self.progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Pronto para download")
        self.progress_label.pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Log de atividades
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(log_frame, text="Log de Atividades:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
    def create_standard_interface(self):
        """Criar interface padrão para YouTube, Instagram, Facebook, TikTok"""
        # Frame padrão
        self.standard_frame = ctk.CTkFrame(self.main_content_frame)
        self.standard_frame.pack(fill="both", expand=True)
        
        # Seleção de plataforma
        platform_frame = ctk.CTkFrame(self.standard_frame)
        platform_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(platform_frame, text="🎯 Selecionar Plataforma:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        platform_select_frame = ctk.CTkFrame(platform_frame)
        platform_select_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.platform_var = tk.StringVar(value="YouTube")
        platform_options = ["YouTube", "Instagram", "Facebook", "TikTok", "Twitch"]
        self.platform_menu = ctk.CTkOptionMenu(
            platform_select_frame, 
            values=platform_options, 
            variable=self.platform_var,
            command=self.on_platform_change,
            width=200
        )
        self.platform_menu.pack(side="left", padx=10, pady=10)
        
        # Descrição da plataforma selecionada
        self.platform_description_label = ctk.CTkLabel(
            platform_select_frame,
            text="📺 YouTube: Opções de qualidade e formato disponíveis",
            font=ctk.CTkFont(size=12),
            text_color=("#ff4444", "#cc3333")
        )
        self.platform_description_label.pack(side="left", padx=20, pady=10)
        
        # URL (oculta para Twitch)
        self.url_frame = ctk.CTkFrame(self.standard_frame)
        self.url_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.url_frame, text="🔗 URL do Vídeo:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        url_input_frame = ctk.CTkFrame(self.url_frame)
        url_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.url_var = tk.StringVar()
        self.url_entry = ctk.CTkEntry(url_input_frame, textvariable=self.url_var, placeholder_text="Cole aqui a URL do vídeo...")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        validate_btn = ctk.CTkButton(url_input_frame, text="✅ Validar", command=self.validate_url, width=100)
        validate_btn.pack(side="right", padx=10, pady=10)
        
        # Pasta de destino
        path_frame = ctk.CTkFrame(self.standard_frame)
        path_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(path_frame, text="📁 Pasta de Destino:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        path_input_frame = ctk.CTkFrame(path_frame)
        path_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        path_entry = ctk.CTkEntry(path_input_frame, textvariable=self.download_path)
        path_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        browse_btn = ctk.CTkButton(path_input_frame, text="📂 Procurar", command=self.browse_folder, width=100)
        browse_btn.pack(side="right", padx=10, pady=10)
        
        # Opções (qualidade e formato) - visível apenas para YouTube
        self.options_frame = ctk.CTkFrame(self.standard_frame)
        self.options_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.options_frame, text="⚙️ Opções de Download:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        options_content_frame = ctk.CTkFrame(self.options_frame)
        options_content_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Qualidade
        quality_frame = ctk.CTkFrame(options_content_frame)
        quality_frame.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkLabel(quality_frame, text="Qualidade:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.quality_var = tk.StringVar(value="best")
        quality_options = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "best"]
        self.quality_menu = ctk.CTkOptionMenu(quality_frame, values=quality_options, variable=self.quality_var)
        self.quality_menu.pack(fill="x", padx=10, pady=(5, 10))
        
        # Formato
        format_frame = ctk.CTkFrame(options_content_frame)
        format_frame.pack(side="right", fill="x", expand=True, padx=(5, 10), pady=10)
        
        ctk.CTkLabel(format_frame, text="Formato:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.format_var = tk.StringVar(value="mp4")
        format_options = ["mp4", "webm", "mkv", "mp3", "m4a"]
        self.format_menu = ctk.CTkOptionMenu(format_frame, values=format_options, variable=self.format_var)
        self.format_menu.pack(fill="x", padx=10, pady=(5, 10))
        
        # Botões de ação (ocultos para Twitch)
        self.action_frame = ctk.CTkFrame(self.standard_frame)
        self.action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        buttons_frame = ctk.CTkFrame(self.action_frame)
        buttons_frame.pack(pady=20)
        
        download_btn = ctk.CTkButton(buttons_frame, text="🚀 Baixar Vídeo", command=self.download_video, height=40, width=200)
        download_btn.pack(side="left", padx=10)
        
        debug_btn = ctk.CTkButton(buttons_frame, text="🔍 Debug Formatos", command=self.debug_formats, height=40, width=150)
        debug_btn.pack(side="left", padx=10)
        
        info_btn = ctk.CTkButton(buttons_frame, text="ℹ️ Info Vídeo", command=self.get_video_info, height=40, width=120)
        info_btn.pack(side="left", padx=10)
        
        # Configurar visibilidade inicial
        self.update_interface_visibility()
    
    def on_platform_change(self, platform):
        """Callback quando a plataforma é alterada"""
        self.log_message(f"🎯 Plataforma selecionada: {platform}")
        
        # Atualizar descrição da plataforma
        platform_descriptions = {
            "YouTube": ("📺 YouTube: Opções de qualidade e formato disponíveis", ("#ff4444", "#cc3333")),
            "Instagram": ("📷 Instagram: Download no formato original", ("#aa44ff", "#8833cc")),
            "Facebook": ("📘 Facebook: Download no formato original", ("#4444ff", "#3333cc")),
            "TikTok": ("🎵 TikTok: Download no formato original", ("#ff44aa", "#cc3388")),
            "Twitch": ("🎮 Twitch: Interface VOD especializada", ("#aa44ff", "#8833cc"))
        }
        
        if platform in platform_descriptions:
            description, color = platform_descriptions[platform]
            self.platform_description_label.configure(text=description, text_color=color)
        
        # Alternar entre interface padrão e Twitch
        if platform == "Twitch":
            self.show_twitch_interface()
        else:
            self.show_standard_interface()
            
        # Atualizar visibilidade da interface
        self.update_interface_visibility()
    
    def update_interface_visibility(self):
        """Atualizar visibilidade dos elementos baseado na plataforma selecionada"""
        platform = self.platform_var.get()
        
        if platform == "Twitch":
            # Para Twitch, ocultar elementos da interface padrão
            self.url_frame.pack_forget()
            self.options_frame.pack_forget()
            self.action_frame.pack_forget()
        else:
            # Para outras plataformas, mostrar elementos relevantes
            self.url_frame.pack(fill="x", padx=20, pady=10, after=self.platform_description_label)
            self.action_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            if platform == "YouTube":
                # Mostrar opções de qualidade e formato para YouTube
                self.options_frame.pack(fill="x", padx=20, pady=(0, 20), before=self.action_frame)
            else:
                # Ocultar opções para Instagram, Facebook e TikTok
                self.options_frame.pack_forget()
    
    def on_url_change(self, *args):
        """Método removido - não mais necessário sem detecção automática"""
        pass
    
    def update_platform_indicator_for_platform(self, platform):
        """Método removido - não mais necessário sem detecção automática"""
        pass
    
    def update_platform_indicator(self, text, color):
        """Método removido - não mais necessário sem detecção automática"""
        pass
    
    def show_twitch_interface(self):
        """Mostrar interface específica do Twitch"""
        self.is_twitch_mode = True
        self.standard_frame.pack_forget()
        self.twitch_interface.show()
        self.log_message("🎮 Modo Twitch ativado - Interface VOD carregada")
    
    def show_standard_interface(self):
        """Mostrar interface padrão"""
        self.is_twitch_mode = False
        self.twitch_interface.hide()
        self.standard_frame.pack(fill="both", expand=True)
        self.log_message(f"📱 Modo {self.platform_var.get().title()} ativado")
    
    def validate_url(self):
        """Validar URL e mostrar informações da plataforma"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Erro", "Por favor, digite uma URL.")
            return
        
        platform = self.platform_var.get()
        
        if platform == "Twitch":
            # Para Twitch, mostrar instruções específicas
            if self.twitch_downloader.validate_url(url):
                self.log_message("✅ URL do Twitch válida")
                self.log_message("💡 Use a interface abaixo para buscar VODs por usuário")
            else:
                self.log_message("❌ URL do Twitch inválida")
                messagebox.showerror("Erro", "URL do Twitch inválida. Use URLs de VODs (ex: https://www.twitch.tv/videos/123456789)")
        elif platform == "YouTube":
            if self.youtube_downloader.validate_url(url):
                self.log_message("✅ URL do YouTube válida")
            else:
                self.log_message("❌ URL do YouTube inválida")
                messagebox.showerror("Erro", "URL do YouTube inválida")
        elif platform == "Instagram":
            if self.instagram_downloader.validate_url(url):
                self.log_message("✅ URL do Instagram válida")
            else:
                self.log_message("❌ URL do Instagram inválida")
                messagebox.showerror("Erro", "URL do Instagram inválida")
        elif platform == "Facebook":
            if self.facebook_downloader.validate_url(url):
                self.log_message("✅ URL do Facebook válida")
            else:
                self.log_message("❌ URL do Facebook inválida")
                messagebox.showerror("Erro", "URL do Facebook inválida")
        elif platform == "TikTok":
            if self.tiktok_downloader.validate_url(url):
                self.log_message("✅ URL do TikTok válida")
            else:
                self.log_message("❌ URL do TikTok inválida")
                messagebox.showerror("Erro", "URL do TikTok inválida")
        else:
            self.log_message("❌ Plataforma não suportada")
            messagebox.showerror("Erro", "Plataforma não suportada. Use URLs do YouTube, Instagram, Facebook, TikTok ou Twitch.")
    
    def download_video(self):
        """Baixar vídeo da plataforma detectada"""
        if self.is_twitch_mode:
            # No modo Twitch, o download é feito pela interface específica
            messagebox.showinfo("Info", "Use a interface do Twitch abaixo para buscar e baixar VODs.")
            return
        
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, digite uma URL.")
            return
        
        platform = self.platform_var.get()
        
        def download_thread():
            try:
                output_path = self.download_path.get()
                
                if platform == "YouTube":
                    quality = self.quality_var.get()
                    format_type = self.format_var.get()
                    
                    self.log_message(f"🚀 Iniciando download do YouTube...")
                    self.log_message(f"📁 Pasta: {output_path}")
                    self.log_message(f"🎯 Qualidade: {quality}")
                    self.log_message(f"📄 Formato: {format_type}")
                    
                    success = self.youtube_downloader.download_video(url, output_path, quality, format_type, self.progress_hook)
                    
                elif platform == "Instagram":
                    self.log_message(f"🚀 Iniciando download do Instagram...")
                    self.log_message(f"📁 Pasta: {output_path}")
                    
                    success = self.instagram_downloader.download_post(url, output_path, self.progress_hook)
                    
                elif platform == "Facebook":
                    self.log_message(f"🚀 Iniciando download do Facebook...")
                    self.log_message(f"📁 Pasta: {output_path}")
                    
                    success = self.facebook_downloader.download_video(url, output_path, self.progress_hook)
                    
                elif platform == "TikTok":
                    self.log_message(f"🚀 Iniciando download do TikTok...")
                    self.log_message(f"📁 Pasta: {output_path}")
                    
                    success = self.tiktok_downloader.download_video(url, output_path, self.progress_hook)
                    
                else:
                    self.log_message("❌ Plataforma não suportada para download direto")
                    messagebox.showerror("Erro", "Plataforma não suportada")
                    return
                
                if success:
                    self.log_message("✅ Download concluído com sucesso!")
                    messagebox.showinfo("Sucesso", "Vídeo baixado com sucesso!")
                else:
                    self.log_message("❌ Falha no download")
                    messagebox.showerror("Erro", "Falha no download")
                    
            except Exception as e:
                error_msg = f"Erro no download: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                messagebox.showerror("Erro", error_msg)
            finally:
                # Resetar barra de progresso
                self.progress_bar.set(0)
        
        # Executar em thread separada
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
    
    def get_video_info(self):
        """Obter informações do vídeo/post"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL válida.")
            return
        
        def fetch_info():
            try:
                self.log_message("Obtendo informações...")
                
                # Obter downloader apropriado
                platform = self.platform_var.get()
                if platform == "YouTube":
                    downloader = self.youtube_downloader
                elif platform == "Instagram":
                    downloader = self.instagram_downloader
                elif platform == "Facebook":
                    downloader = self.facebook_downloader
                elif platform == "TikTok":
                    downloader = self.tiktok_downloader
                else:  # Twitch
                    downloader = self.twitch_downloader
                
                # Validar URL
                if not downloader.validate_url(url):
                    self.log_message(f"❌ URL não é válida para {platform}")
                    
                    # Para Facebook, dar dicas específicas
                    if platform == "Facebook":
                        self.log_message("💡 Dicas para URLs do Facebook:")
                        self.log_message("   • Certifique-se de que o vídeo é público")
                        self.log_message("   • Tente usar a URL completa (não encurtada)")
                        self.log_message("   • Verifique se você consegue ver o vídeo sem fazer login")
                        self.log_message("   • Use o botão 'Debug Formatos' para mais detalhes")
                    elif platform == "TikTok":
                        self.log_message("💡 Dicas para URLs do TikTok:")
                        self.log_message("   • Certifique-se de que o vídeo é público")
                        self.log_message("   • Tente usar a URL completa do TikTok")
                        self.log_message("   • URLs encurtadas (vm.tiktok.com) também funcionam")
                        self.log_message("   • Use o botão 'Debug Formatos' para mais detalhes")
                    
                    return
                
                # Obter informações
                info = downloader.get_video_info(url)
                if info:
                    if platform == "Instagram":
                        post_type = self.instagram_downloader.get_post_type(url)
                        self.log_message(f"📱 {post_type.title()} do Instagram encontrado!")
                        self.log_message(f"👤 Autor: {info.get('uploader', 'N/A')}")
                        self.log_message(f"📝 Título: {info.get('title', 'N/A')}")
                        if info.get('duration', 0) > 0:
                            self.log_message(f"⏱️ Duração: {info['duration']}s")
                        
                        # Verificar se é carrossel
                        entries = info.get('entries', [])
                        if entries:
                            self.log_message(f"📸 Carrossel com {len(entries)} itens")
                    elif platform == "Facebook":
                        video_type = self.facebook_downloader.get_video_type(url)
                        self.log_message(f"📘 {video_type.title()} do Facebook encontrado!")
                        self.log_message(f"👤 Autor: {info.get('uploader', 'N/A')}")
                        self.log_message(f"📝 Título: {info.get('title', 'N/A')}")
                        if info.get('duration', 0) > 0:
                            self.log_message(f"⏱️ Duração: {info['duration']}s")
                        if info.get('view_count'):
                            self.log_message(f"👀 Visualizações: {info['view_count']}")
                    elif platform == "TikTok":
                        video_type = self.tiktok_downloader.get_video_type(url)
                        self.log_message(f"🎵 {video_type.title()} do TikTok encontrado!")
                        self.log_message(f"👤 Autor: {info.get('uploader', 'N/A')}")
                        self.log_message(f"📝 Título: {info.get('title', 'N/A')}")
                        if info.get('duration', 0) > 0:
                            self.log_message(f"⏱️ Duração: {info['duration']}s")
                        if info.get('view_count'):
                            self.log_message(f"👀 Visualizações: {info['view_count']}")
                        if info.get('like_count'):
                            self.log_message(f"❤️ Curtidas: {info['like_count']}")
                    else:  # YouTube
                        self.log_message(f"📺 Vídeo encontrado: {info.get('title', 'N/A')}")
                        self.log_message(f"👤 Canal: {info.get('uploader', 'N/A')}")
                        self.log_message(f"⏱️ Duração: {info.get('duration_string', 'N/A')}")
                        self.log_message(f"👀 Visualizações: {info.get('view_count', 'N/A')}")
                else:
                    self.log_message("❌ Não foi possível obter informações")
                    
            except Exception as e:
                self.log_message(f"❌ Erro: {str(e)}")
        
        # Executar em thread separada
        thread = threading.Thread(target=fetch_info)
        thread.daemon = True
        thread.start()
    
    def debug_formats(self):
        """Debug: Analisar formatos disponíveis"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL válida.")
            return
        
        def debug():
            try:
                # Obter downloader apropriado
                platform = self.platform_var.get()
                if platform == "YouTube":
                    downloader = self.youtube_downloader
                elif platform == "Instagram":
                    downloader = self.instagram_downloader
                elif platform == "Facebook":
                    downloader = self.facebook_downloader
                elif platform == "TikTok":
                    downloader = self.tiktok_downloader
                else:  # Twitch
                    downloader = self.twitch_downloader
                
                self.log_message(f"🔍 Analisando formatos do {platform}...")
                
                # Executar debug baseado na plataforma
                if platform == "Instagram":
                    downloader.debug_formats(url)
                elif platform == "Facebook":
                    downloader.debug_formats(url)
                    
                    # Também testar acesso à URL do Facebook
                    self.log_message("🔍 Testando acesso à URL do Facebook...")
                    test_result = downloader.test_url_access(url)
                    if test_result['accessible']:
                        self.log_message(f"✅ URL acessível: {test_result['message']}")
                    else:
                        self.log_message(f"❌ Problema com URL: {test_result['message']}")
                elif platform == "TikTok":
                    downloader.debug_formats(url)
                    
                    # Também testar acesso à URL do TikTok
                    self.log_message("🔍 Testando acesso à URL do TikTok...")
                    test_result = downloader.test_url_access(url)
                    if test_result['accessible']:
                        self.log_message(f"✅ URL acessível: {test_result['message']}")
                    else:
                        self.log_message(f"❌ Problema com URL: {test_result['message']}")
                else:  # YouTube
                    downloader.debug_formats(url)
                    
                    # Também executar teste de qualidade para YouTube
                    current_quality = self.quality_var.get()
                    self.log_message(f"Testando seleção de qualidade para {current_quality}...")
                    downloader.test_quality_selection(url, current_quality)
                
                self.log_message("Análise de formatos concluída! Verifique o console.")
            except Exception as e:
                self.log_message(f"❌ Erro no debug: {str(e)}")
        
        # Executar em thread separada
        thread = threading.Thread(target=debug)
        thread.daemon = True
        thread.start()
    
    def browse_folder(self):
        """Abrir diálogo para selecionar pasta de destino"""
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
    
    def log_message(self, message):
        """Adicionar mensagem ao log"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def update_progress(self, percentage, status=""):
        """Atualizar barra de progresso"""
        self.progress_bar.set(percentage / 100)
        if status:
            self.progress_label.configure(text=status)
        self.root.update_idletasks()
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.root.after(0, lambda: self.update_progress(percentage, f"Baixando... {percentage:.1f}%"))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.update_progress(100, "Download concluído!"))
    
    def run(self):
        """Executar aplicativo"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.run()
