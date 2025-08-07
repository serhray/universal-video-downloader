import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
from twitch_downloader import TwitchDownloader


class TwitchVODInterface:
    """Interface específica para busca e download de VODs do Twitch"""
    
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.twitch_downloader = TwitchDownloader()
        self.selected_vod = None
        self.vods_list = []
        
    def create_twitch_interface(self, parent_frame):
        """
        Criar interface específica para Twitch
        
        Args:
            parent_frame: Frame pai onde criar a interface
        """
        # Frame principal do Twitch
        self.twitch_frame = ctk.CTkFrame(parent_frame)
        
        # Título
        title_label = ctk.CTkLabel(
            self.twitch_frame, 
            text="🎮 Twitch VOD Downloader", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Frame de busca
        search_frame = ctk.CTkFrame(self.twitch_frame)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # Nome do usuário
        ctk.CTkLabel(search_frame, text="Nome do Streamer:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10, 5))
        
        username_frame = ctk.CTkFrame(search_frame)
        username_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.username_var = tk.StringVar()
        self.username_entry = ctk.CTkEntry(username_frame, textvariable=self.username_var, placeholder_text="Ex: ninja, shroud, pokimane")
        self.username_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        # Quantidade de VODs
        ctk.CTkLabel(username_frame, text="Qtd:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 5), pady=10)
        
        self.vod_count_var = tk.StringVar(value="10")
        vod_count_options = ["5", "10", "15", "20", "25"]
        self.vod_count_menu = ctk.CTkOptionMenu(username_frame, values=vod_count_options, variable=self.vod_count_var, width=60)
        self.vod_count_menu.pack(side="left", padx=(0, 10), pady=10)
        
        # Botão de busca
        search_btn = ctk.CTkButton(username_frame, text="🔍 Buscar VODs", command=self.search_vods, width=120)
        search_btn.pack(side="right", padx=10, pady=10)
        
        # Frame da lista de VODs
        vods_frame = ctk.CTkFrame(self.twitch_frame)
        vods_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(vods_frame, text="VODs Encontrados:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Lista de VODs (usando Textbox como lista)
        self.vods_textbox = ctk.CTkTextbox(vods_frame, height=150)
        self.vods_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Frame de seleção de VOD
        selection_frame = ctk.CTkFrame(self.twitch_frame)
        selection_frame.pack(fill="x", padx=20, pady=10)
        
        # Seleção do VOD
        select_frame = ctk.CTkFrame(selection_frame)
        select_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(select_frame, text="Selecionar VOD:", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.vod_index_var = tk.StringVar(value="1")
        self.vod_index_entry = ctk.CTkEntry(select_frame, textvariable=self.vod_index_var, width=50, placeholder_text="1")
        self.vod_index_entry.pack(side="left", padx=10)
        
        select_btn = ctk.CTkButton(select_frame, text="✅ Selecionar", command=self.select_vod, width=100)
        select_btn.pack(side="left", padx=10)
        
        # Frame de configuração do download
        config_frame = ctk.CTkFrame(self.twitch_frame)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        # Nome personalizado (opcional)
        name_frame = ctk.CTkFrame(config_frame)
        name_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(name_frame, text="Nome do Arquivo (opcional):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.custom_name_var = tk.StringVar()
        self.custom_name_entry = ctk.CTkEntry(name_frame, textvariable=self.custom_name_var, placeholder_text="Ex: MelhorMomento_Ninja")
        self.custom_name_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Tempos de início e fim (obrigatórios)
        time_frame = ctk.CTkFrame(config_frame)
        time_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(time_frame, text="Recorte de Tempo (obrigatório):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10, 5))
        
        time_inputs_frame = ctk.CTkFrame(time_frame)
        time_inputs_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Tempo de início
        ctk.CTkLabel(time_inputs_frame, text="Início:", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.start_time_var = tk.StringVar()
        self.start_time_entry = ctk.CTkEntry(time_inputs_frame, textvariable=self.start_time_var, width=100, placeholder_text="00:30")
        self.start_time_entry.pack(side="left", padx=(0, 20))
        
        # Tempo de fim
        ctk.CTkLabel(time_inputs_frame, text="Fim:", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.end_time_var = tk.StringVar()
        self.end_time_entry = ctk.CTkEntry(time_inputs_frame, textvariable=self.end_time_var, width=100, placeholder_text="05:30")
        self.end_time_entry.pack(side="left", padx=(0, 20))
        
        # Dica de formato
        ctk.CTkLabel(time_inputs_frame, text="(Formato: MM:SS ou HH:MM:SS)", font=ctk.CTkFont(size=10)).pack(side="left", padx=10)
        
        # Botão de download
        download_btn = ctk.CTkButton(self.twitch_frame, text="🚀 Baixar Segmento", command=self.download_segment, height=40)
        download_btn.pack(pady=20)
        
        return self.twitch_frame
    
    def search_vods(self):
        """Buscar VODs do usuário"""
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Erro", "Por favor, digite o nome do streamer.")
            return
        
        if not self.twitch_downloader.validate_username(username):
            messagebox.showerror("Erro", "Nome de usuário inválido. Use apenas letras, números e underscore (4-25 caracteres).")
            return
        
        def search_thread():
            try:
                self.parent_app.log_message(f"🔍 Buscando VODs de {username}...")
                
                max_vods = int(self.vod_count_var.get())
                vods = self.twitch_downloader.search_user_vods(username, max_vods)
                
                if vods:
                    self.vods_list = vods
                    self.display_vods(vods)
                    self.parent_app.log_message(f"✅ Encontrados {len(vods)} VODs de {username}")
                else:
                    self.parent_app.log_message(f"❌ Nenhum VOD encontrado para {username}")
                    self.vods_textbox.delete("1.0", "end")
                    self.vods_textbox.insert("1.0", "Nenhum VOD encontrado. Verifique se o nome do usuário está correto.")
                    
            except Exception as e:
                self.parent_app.log_message(f"❌ Erro na busca: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao buscar VODs: {str(e)}")
        
        # Executar em thread separada
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
    
    def display_vods(self, vods):
        """Exibir lista de VODs na interface"""
        self.vods_textbox.delete("1.0", "end")
        
        for vod in vods:
            vod_info = self.twitch_downloader.format_vod_info(vod)
            self.vods_textbox.insert("end", vod_info + "\n")
    
    def select_vod(self):
        """Selecionar um VOD da lista"""
        try:
            index = int(self.vod_index_var.get())
            
            if not self.vods_list:
                messagebox.showerror("Erro", "Primeiro busque VODs de um usuário.")
                return
            
            if index < 1 or index > len(self.vods_list):
                messagebox.showerror("Erro", f"Índice inválido. Escolha entre 1 e {len(self.vods_list)}.")
                return
            
            self.selected_vod = self.vods_list[index - 1]
            
            # Exibir informações do VOD selecionado
            vod_info = self.twitch_downloader.format_vod_info(self.selected_vod)
            self.parent_app.log_message(f"✅ VOD selecionado: {vod_info}")
            
            # Sugerir nome do arquivo baseado no título
            title = self.selected_vod.get('title', 'VOD')
            # Limpar caracteres especiais do título
            clean_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            self.custom_name_var.set(clean_title)
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, digite um número válido.")
    
    def download_segment(self):
        """Baixar segmento do VOD selecionado"""
        if not self.selected_vod:
            messagebox.showerror("Erro", "Primeiro selecione um VOD da lista.")
            return
        
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        
        if not start_time or not end_time:
            messagebox.showerror("Erro", "Por favor, defina os tempos de início e fim.")
            return
        
        # Validar formato de tempo
        if not self._validate_time_format(start_time) or not self._validate_time_format(end_time):
            messagebox.showerror("Erro", "Formato de tempo inválido. Use MM:SS ou HH:MM:SS (ex: 01:30 ou 01:30:45)")
            return
        
        def download_thread():
            try:
                output_path = self.parent_app.download_path.get()
                custom_name = self.custom_name_var.get().strip() or None
                
                self.parent_app.log_message(f"🚀 Iniciando download do segmento do Twitch...")
                self.parent_app.log_message(f"📁 Pasta: {output_path}")
                self.parent_app.log_message(f"🎮 VOD: {self.selected_vod['title']}")
                self.parent_app.log_message(f"⏰ Segmento: {start_time} → {end_time}")
                if custom_name:
                    self.parent_app.log_message(f"📝 Nome personalizado: {custom_name}")
                
                success = self.twitch_downloader.download_vod_segment(
                    self.selected_vod['url'],
                    output_path,
                    start_time,
                    end_time,
                    custom_name,
                    self.parent_app.progress_hook
                )
                
                if success:
                    self.parent_app.log_message("✅ Download do segmento concluído com sucesso!")
                    messagebox.showinfo("Sucesso", "Segmento do VOD baixado com sucesso!")
                else:
                    self.parent_app.log_message("❌ Falha no download do segmento")
                    messagebox.showerror("Erro", "Falha no download do segmento")
                    
            except Exception as e:
                error_msg = f"Erro no download: {str(e)}"
                self.parent_app.log_message(f"❌ {error_msg}")
                messagebox.showerror("Erro", error_msg)
            finally:
                # Resetar barra de progresso
                self.parent_app.progress_bar.set(0)
        
        # Executar em thread separada
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
    
    def _validate_time_format(self, time_str):
        """Validar formato de tempo"""
        import re
        # Aceitar MM:SS ou HH:MM:SS
        pattern = r'^(\d{1,2}):([0-5]\d)$|^(\d{1,2}):([0-5]\d):([0-5]\d)$'
        return bool(re.match(pattern, time_str))
    
    def show(self):
        """Mostrar interface do Twitch"""
        self.twitch_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def hide(self):
        """Ocultar interface do Twitch"""
        self.twitch_frame.pack_forget()
