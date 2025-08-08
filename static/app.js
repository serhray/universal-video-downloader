// Universal Video Downloader Web App - Frontend JavaScript
class VideoDownloaderApp {
    constructor() {
        // Detectar se está no ambiente Vercel
        this.isVercel = window.location.hostname.includes('vercel.app') || 
                       window.location.hostname.includes('vercel.com');
        
        // Inicializar WebSocket apenas se não estiver no Vercel
        if (!this.isVercel) {
            this.socket = io();
            this.setupWebSocket();
        } else {
            this.socket = null;
            console.log(' Ambiente Vercel detectado - WebSocket desabilitado');
        }
        
        this.currentDownloadId = null;
        this.selectedVod = null;
        this.vods = [];
        this.downloadFiles = []; // Adicionar propriedade para armazenar arquivos
        
        this.initializeElements();
        this.bindEvents();
        
        // Apply default theme
        this.applyPlatformTheme('YouTube');
        
        this.log(' Aplicação web carregada');
        if (this.isVercel) {
            this.log(' Modo Vercel: usando HTTP direto');
        } else {
            this.log(' Modo local: usando WebSocket');
        }
        this.log(' Sistema de temas ativado');
        this.log(' Selecione uma plataforma e cole a URL para começar');
    }
    
    initializeElements() {
        // Platform elements
        this.platformSelect = document.getElementById('platformSelect');
        this.platformIndicator = document.getElementById('platformIndicator');
        
        // Interface elements
        this.standardInterface = document.getElementById('standardInterface');
        this.twitchInterface = document.getElementById('twitchInterface');
        
        // Standard interface elements
        this.videoUrl = document.getElementById('videoUrl');
        this.validateBtn = document.getElementById('validateBtn');
        this.optionsCard = document.getElementById('optionsCard');
        this.qualitySelect = document.getElementById('qualitySelect');
        this.formatSelect = document.getElementById('formatSelect');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.infoBtn = document.getElementById('infoBtn');
        
        // Twitch interface elements
        this.twitchUsername = document.getElementById('twitchUsername');
        this.vodCount = document.getElementById('vodCount');
        this.searchVodsBtn = document.getElementById('searchVodsBtn');
        this.vodsListCard = document.getElementById('vodsListCard');
        this.vodsList = document.getElementById('vodsList');
        this.vodConfigCard = document.getElementById('vodConfigCard');
        this.customName = document.getElementById('customName');
        this.startTime = document.getElementById('startTime');
        this.endTime = document.getElementById('endTime');
        this.downloadSegmentBtn = document.getElementById('downloadSegmentBtn');
        
        // Progress elements
        this.progressCard = document.getElementById('progressCard');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.downloadFileBtn = document.getElementById('downloadFileBtn');
        
        // Info elements
        this.videoInfoCard = document.getElementById('videoInfoCard');
        this.videoInfoContent = document.getElementById('videoInfoContent');
    }
    
    bindEvents() {
        // Platform selection
        this.platformSelect.addEventListener('change', () => this.onPlatformChange());
        
        // Standard interface events
        this.validateBtn.addEventListener('click', () => this.validateUrl());
        this.downloadBtn.addEventListener('click', () => this.downloadVideo());
        this.infoBtn.addEventListener('click', () => this.getVideoInfo());
        
        // Twitch interface events
        this.searchVodsBtn.addEventListener('click', () => this.searchVods());
        this.downloadSegmentBtn.addEventListener('click', () => this.downloadSegment());
        
        // Progress events
        this.downloadFileBtn.addEventListener('click', () => this.downloadFile());
        
        // Enter key support
        this.videoUrl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.validateUrl();
        });
        
        // Hide video info when URL is cleared
        this.videoUrl.addEventListener('input', (e) => {
            if (e.target.value.trim() === '') {
                this.hideVideoInfo();
            }
        });
        
        this.twitchUsername.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchVods();
        });
    }
    
    setupWebSocket() {
        this.socket.on('connect', () => {
            this.log(' Conectado ao servidor');
        });
        
        this.socket.on('disconnect', () => {
            this.log(' Desconectado do servidor');
        });
        
        this.socket.on('download_progress', (data) => {
            if (data.download_id === this.currentDownloadId) {
                this.updateProgress(data.progress, data.status);
            }
        });
        
        this.socket.on('download_complete', (data) => {
            if (data.download_id === this.currentDownloadId) {
                this.log(' ' + data.message);
                this.updateProgress(100, 'completed');
                this.downloadFileBtn.style.display = 'block';
            }
        });
        
        this.socket.on('download_error', (data) => {
            if (data.download_id === this.currentDownloadId) {
                this.log(' ' + data.message);
                this.updateProgress(0, 'error');
                this.showAlert('Erro no download: ' + data.message, 'danger');
            }
        });
    }
    
    onPlatformChange() {
        const platform = this.platformSelect.value;
        this.log(` Plataforma selecionada: ${platform}`);
        
        // Apply platform theme to body
        this.applyPlatformTheme(platform);
        
        // Update platform indicator
        const indicators = {
            'YouTube': {
                text: ' YouTube: Opções de qualidade e formato disponíveis',
                class: 'platform-youtube',
                emoji: ''
            },
            'Instagram': {
                text: ' Instagram: Download no formato original',
                class: 'platform-instagram',
                emoji: ''
            },
            'Facebook': {
                text: ' Facebook: Download no formato original',
                class: 'platform-facebook',
                emoji: ''
            },
            'TikTok': {
                text: ' TikTok: Download no formato original',
                class: 'platform-tiktok',
                emoji: ''
            },
            'Twitch': {
                text: ' Twitch: Interface VOD especializada',
                class: 'platform-twitch',
                emoji: ''
            }
        };
        
        const indicator = indicators[platform];
        this.platformIndicator.textContent = `${indicator.emoji} ${indicator.text}`;
        this.platformIndicator.className = `platform-indicator ${indicator.class}`;
        
        // Switch interfaces
        if (platform === 'Twitch') {
            this.showTwitchInterface();
        } else {
            this.showStandardInterface();
        }
        
        // Update options visibility
        this.updateOptionsVisibility(platform);
        
        // Log platform theme change
        this.log(` Tema ${platform} aplicado`);
    }
    
    applyPlatformTheme(platform) {
        // Remove all existing theme classes
        document.body.classList.remove(
            'theme-youtube',
            'theme-instagram', 
            'theme-facebook',
            'theme-tiktok',
            'theme-twitch'
        );
        
        // Apply new theme class
        const themeClass = `theme-${platform.toLowerCase()}`;
        document.body.classList.add(themeClass);
        
        // Update page title with platform emoji
        const platformEmojis = {
            'YouTube': '',
            'Instagram': '',
            'Facebook': '',
            'TikTok': '',
            'Twitch': ''
        };
        
        const emoji = platformEmojis[platform] || '';
        document.title = `${emoji} Universal Video Downloader - ${platform}`;
        
        // Add subtle animation effect
        document.body.style.animation = 'themeTransition 0.5s ease-out';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 500);
    }
    
    showStandardInterface() {
        this.standardInterface.style.display = 'block';
        this.twitchInterface.style.display = 'none';
        this.log(' Interface padrão ativada');
    }
    
    showTwitchInterface() {
        this.standardInterface.style.display = 'none';
        this.twitchInterface.style.display = 'block';
        this.log(' Interface Twitch ativada');
    }
    
    updateOptionsVisibility(platform) {
        if (platform === 'YouTube') {
            this.optionsCard.style.display = 'block';
        } else {
            this.optionsCard.style.display = 'none';
        }
    }
    
    async validateUrl() {
        const url = this.videoUrl.value.trim();
        const platform = this.platformSelect.value;
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        this.setButtonLoading(this.validateBtn, true);
        
        try {
            const response = await fetch('/api/validate_url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, platform })
            });
            
            const data = await response.json();
            
            if (data.valid) {
                this.log(` ${data.message}`);
                this.showAlert(data.message, 'success');
            } else {
                this.log(` ${data.message}`);
                this.showAlert(data.message, 'danger');
            }
        } catch (error) {
            this.log(` Erro na validação: ${error.message}`);
            this.showAlert('Erro na validação', 'danger');
        } finally {
            this.setButtonLoading(this.validateBtn, false);
        }
    }
    
    async downloadVideo() {
        const url = this.videoUrl.value.trim();
        const platform = this.platformSelect.value;
        const quality = this.qualitySelect.value;
        const format = this.formatSelect.value;
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        this.setButtonLoading(this.downloadBtn, true);
        this.progressCard.style.display = 'block';
        this.updateProgress(0, 'starting');
        
        try {
            // Mostrar progresso simulado no Vercel
            if (this.isVercel) {
                this.log(' Processando download no servidor...');
                this.updateProgress(50, 'processing');
            }
            
            const response = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, platform, quality, format })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentDownloadId = data.download_id;
                this.downloadFiles = data.files; // Armazenar arquivos para download
                
                this.log(` ${data.message}`);
                this.log(` Plataforma: ${platform}`);
                if (platform === 'YouTube') {
                    this.log(` Qualidade: ${quality}`);
                    this.log(` Formato: ${format}`);
                }
                
                // Se estiver no Vercel, mostrar resultado correto
                if (this.isVercel) {
                    this.log(' Download concluído com sucesso!');
                    this.updateProgress(100, 'completed');
                    this.downloadFileBtn.style.display = 'block';
                    
                    // Mostrar informações dos arquivos
                    if (data.files && data.files.length > 0) {
                        data.files.forEach(file => {
                            this.log(` Arquivo: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
                        });
                    }
                }
            } else {
                this.log(` ${data.message}`);
                this.showAlert(data.message, 'danger');
                this.progressCard.style.display = 'none';
            }
        } catch (error) {
            this.log(` Erro no download: ${error.message}`);
            this.showAlert('Erro no download', 'danger');
            this.progressCard.style.display = 'none';
        } finally {
            this.setButtonLoading(this.downloadBtn, false);
        }
    }
    
    async getVideoInfo() {
        const url = this.videoUrl.value.trim();
        const platform = this.platformSelect.value;
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        this.setButtonLoading(this.infoBtn, true);
        
        try {
            const response = await fetch('/api/get_video_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, platform })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayVideoInfo(data.info);
                this.log(' Informações do vídeo obtidas');
            } else {
                this.log(` ${data.message}`);
                this.showAlert(data.message, 'danger');
            }
        } catch (error) {
            this.log(` Erro ao obter informações: ${error.message}`);
            this.showAlert('Erro ao obter informações', 'danger');
        } finally {
            this.setButtonLoading(this.infoBtn, false);
        }
    }
    
    displayVideoInfo(info) {
        let content = ``;
        
        // Adicionar thumbnail se disponível
        if (info.thumbnail) {
            content += `
                <div class="row mb-4">
                    <div class="col-12 text-center">
                        <img src="${info.thumbnail}" 
                             alt="Thumbnail do vídeo" 
                             class="video-thumbnail img-fluid rounded shadow"
                             style="max-width: 100%; max-height: 300px; object-fit: cover;"
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div class="thumbnail-error" style="display: none; padding: 20px; background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; margin: 10px 0;">
                            <i class="bi bi-image" style="font-size: 2rem; color: var(--text-secondary);"></i>
                            <p style="margin-top: 10px; color: var(--text-secondary);">
                                Thumbnail não disponível para esta ${info.platform} post
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        content += `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="bi bi-play-circle"></i> Título:</h6>
                    <p>${info.title}</p>
                    
                    <h6><i class="bi bi-person-circle"></i> Autor:</h6>
                    <p>${info.uploader}</p>
                </div>
                <div class="col-md-6">
        `;
        
        if (info.duration > 0) {
            const duration = this.formatDuration(info.duration);
            content += `
                <h6><i class="bi bi-clock"></i> Duração:</h6>
                <p>${duration}</p>
            `;
        }
        
        if (info.view_count > 0) {
            content += `
                <h6><i class="bi bi-eye"></i> Visualizações:</h6>
                <p>${info.view_count.toLocaleString()}</p>
            `;
        }
        
        // Platform specific info
        if (info.post_type) {
            content += `
                <h6><i class="bi bi-tag"></i> Tipo:</h6>
                <p>${info.post_type}</p>
            `;
        }
        
        if (info.carousel_count) {
            content += `
                <h6><i class="bi bi-images"></i> Carrossel:</h6>
                <p>${info.carousel_count} itens</p>
            `;
        }
        
        if (info.like_count > 0) {
            content += `
                <h6><i class="bi bi-heart"></i> Curtidas:</h6>
                <p>${info.like_count.toLocaleString()}</p>
            `;
        }
        
        content += `
                </div>
            </div>
        `;
        
        this.videoInfoContent.innerHTML = content;
        this.videoInfoCard.style.display = 'block';
    }
    
    async searchVods() {
        const username = this.twitchUsername.value.trim();
        const maxVods = parseInt(this.vodCount.value);
        
        if (!username) {
            this.showAlert('Por favor, digite o nome do streamer', 'warning');
            return;
        }
        
        this.setButtonLoading(this.searchVodsBtn, true);
        
        try {
            const response = await fetch('/api/twitch/search_vods', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, max_vods: maxVods })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.vods = data.vods;
                this.displayVods(data.vods);
                this.log(` Encontrados ${data.count} VODs de ${username}`);
            } else {
                this.log(` ${data.message}`);
                this.showAlert(data.message, 'danger');
                this.vodsListCard.style.display = 'none';
            }
        } catch (error) {
            this.log(` Erro na busca: ${error.message}`);
            this.showAlert('Erro na busca de VODs', 'danger');
        } finally {
            this.setButtonLoading(this.searchVodsBtn, false);
        }
    }
    
    displayVods(vods) {
        let content = '';
        
        vods.forEach((vod, index) => {
            content += `
                <div class="vod-item" data-index="${index}" onclick="app.selectVod(${index})">
                    <div class="row align-items-center">
                        <div class="col-1">
                            <strong>#${vod.index}</strong>
                        </div>
                        <div class="col-3">
                            ${vod.thumbnail ? `
                                <img src="${vod.thumbnail}" 
                                     alt="Thumbnail do VOD" 
                                     class="vod-thumbnail img-fluid rounded shadow"
                                     style="max-width: 100%; max-height: 80px; object-fit: cover;"
                                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                                <div class="thumbnail-placeholder" style="display: none; padding: 10px; background-color: rgba(156, 39, 176, 0.1); border-radius: 8px; text-align: center;">
                                    <i class="bi bi-play-circle" style="font-size: 1.5rem; color: var(--twitch-primary);"></i>
                                </div>
                            ` : `
                                <div class="thumbnail-placeholder" style="padding: 10px; background-color: rgba(156, 39, 176, 0.1); border-radius: 8px; text-align: center;">
                                    <i class="bi bi-play-circle" style="font-size: 1.5rem; color: var(--twitch-primary);"></i>
                                </div>
                            `}
                        </div>
                        <div class="col-5">
                            <h6 class="mb-1">${vod.title}</h6>
                            <small class="text-muted"> ${vod.upload_date}</small>
                        </div>
                        <div class="col-2">
                            <small> ${vod.duration}</small>
                        </div>
                        <div class="col-1">
                            <small> ${vod.view_count.toLocaleString()}</small>
                        </div>
                    </div>
                </div>
            `;
        });
        
        this.vodsList.innerHTML = content;
        this.vodsListCard.style.display = 'block';
    }
    
    selectVod(index) {
        // Remove previous selection
        document.querySelectorAll('.vod-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Add selection to clicked item
        const selectedItem = document.querySelector(`[data-index="${index}"]`);
        selectedItem.classList.add('selected');
        
        // Store selected VOD
        this.selectedVod = this.vods[index];
        
        // Suggest filename based on title
        const cleanTitle = this.selectedVod.title
            .replace(/[^a-zA-Z0-9\s\-_]/g, '')
            .substring(0, 30)
            .trim();
        this.customName.value = cleanTitle;
        
        // Show configuration card
        this.vodConfigCard.style.display = 'block';
        
        this.log(` VOD selecionado: ${this.selectedVod.title}`);
    }
    
    async downloadSegment() {
        if (!this.selectedVod) {
            this.showAlert('Por favor, selecione um VOD primeiro', 'warning');
            return;
        }
        
        const startTime = this.startTime.value.trim();
        const endTime = this.endTime.value.trim();
        const customName = this.customName.value.trim() || null;
        
        if (!startTime || !endTime) {
            this.showAlert('Por favor, defina os tempos de início e fim', 'warning');
            return;
        }
        
        // Validate time format
        const timeRegex = /^(\d{1,2}):([0-5]\d)(:([0-5]\d))?$/;
        if (!timeRegex.test(startTime) || !timeRegex.test(endTime)) {
            this.showAlert('Formato de tempo inválido. Use MM:SS ou HH:MM:SS', 'warning');
            return;
        }
        
        this.setButtonLoading(this.downloadSegmentBtn, true);
        this.progressCard.style.display = 'block';
        this.updateProgress(0, 'starting');
        
        try {
            const response = await fetch('/api/twitch/download_segment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    vod_url: this.selectedVod.url,
                    start_time: startTime,
                    end_time: endTime,
                    custom_name: customName
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentDownloadId = data.download_id;
                this.log(` ${data.message}`);
                this.log(` VOD: ${this.selectedVod.title}`);
                this.log(` Segmento: ${startTime} → ${endTime}`);
                if (customName) {
                    this.log(` Nome personalizado: ${customName}`);
                }
                
                // Se estiver no Vercel, mostrar resultado correto
                if (this.isVercel) {
                    this.log(' Download concluído com sucesso!');
                    this.updateProgress(100, 'completed');
                    this.downloadFileBtn.style.display = 'block';
                }
            } else {
                this.log(` ${data.message}`);
                this.showAlert(data.message, 'danger');
                this.progressCard.style.display = 'none';
            }
        } catch (error) {
            this.log(` Erro no download: ${error.message}`);
            this.showAlert('Erro no download do segmento', 'danger');
            this.progressCard.style.display = 'none';
        } finally {
            this.setButtonLoading(this.downloadSegmentBtn, false);
        }
    }
    
    downloadFile() {
        if (this.isVercel && this.downloadFiles && this.downloadFiles.length > 0) {
            // No Vercel, usar os arquivos da resposta HTTP
            const file = this.downloadFiles[0]; // Pegar o primeiro arquivo
            window.open(file.download_url, '_blank');
            this.log(` Iniciando download: ${file.name}`);
        } else if (this.currentDownloadId) {
            // Modo local (WebSocket)
            window.open(`/api/download_file/${this.currentDownloadId}`, '_blank');
            this.log(' Iniciando download do arquivo');
        }
    }
    
    updateProgress(percentage, status) {
        const roundedPercentage = Math.round(percentage);
        this.progressBar.style.width = `${roundedPercentage}%`;
        this.progressText.textContent = `${roundedPercentage}%`;
        
        if (status === 'completed') {
            this.progressBar.classList.remove('bg-primary');
            this.progressBar.classList.add('bg-success');
        } else if (status === 'error') {
            this.progressBar.classList.remove('bg-primary');
            this.progressBar.classList.add('bg-danger');
        }
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.setAttribute('data-original-text', originalText);
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
        } else {
            button.disabled = false;
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.innerHTML = originalText;
            }
        }
    }
    
    showAlert(message, type) {
        // Create alert element with platform-specific styling
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show platform-alert`;
        
        // Add platform-specific icon
        const currentPlatform = this.platformSelect.value;
        const platformIcons = {
            'YouTube': '',
            'Instagram': '',
            'Facebook': '',
            'TikTok': '',
            'Twitch': ''
        };
        
        const icon = platformIcons[currentPlatform] || '';
        
        alertDiv.innerHTML = `
            <strong>${icon} ${currentPlatform}:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of main container
        const mainContainer = document.querySelector('.main-container');
        mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        
        logEntry.className = 'text-light';
        logEntry.innerHTML = `[${timestamp}] ${message}`;
        
        // this.logContainer.appendChild(logEntry);
        
        // Auto-scroll to bottom
        // this.logContainer.scrollTop = this.logContainer.scrollHeight;
        
        // Keep only last 100 log entries
        // while (this.logContainer.children.length > 100) {
        //     this.logContainer.removeChild(this.logContainer.firstChild);
        // }
    }
    
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
    
    hideVideoInfo() {
        this.videoInfoCard.style.display = 'none';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VideoDownloaderApp();
});
