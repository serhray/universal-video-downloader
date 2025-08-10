// Universal Video Downloader Web App - Frontend JavaScript
class VideoDownloaderApp {
    constructor() {
        // FORÇAR MODO HTTP - SEM SOCKETIO (backend limpo)
        this.isVercel = true; // Forçar modo HTTP sempre
        this.socket = null; // Nunca usar SocketIO
        
        console.log(' Modo HTTP forçado - SocketIO desabilitado');
        
        this.currentDownloadId = null;
        this.selectedTweet = null;
        this.tweets = [];
        this.downloadFiles = [];
        this.initializeElements();
        this.bindEvents();
        
        // Apply default theme
        this.applyPlatformTheme('Instagram');
        
        this.log(' Aplicação web carregada');
        this.log(' Plataformas: Instagram, Facebook, TikTok, X/Twitter');
        this.log(' Modo HTTP: usando endpoints REST');
        this.log(' Sistema de temas ativado');
        this.log(' Selecione uma plataforma e cole a URL para começar');
    }
    
    initializeElements() {
        // Platform elements
        this.platformSelect = document.getElementById('platformSelect');
        this.platformIndicator = document.getElementById('platformIndicator');
        
        // Interface elements
        this.standardInterface = document.getElementById('standardInterface');
        this.xTwitterInterface = document.getElementById('xTwitterInterface');
        
        // Standard interface elements
        this.videoUrl = document.getElementById('videoUrl');
        this.validateBtn = document.getElementById('validateBtn');
        this.optionsCard = document.getElementById('optionsCard');
        this.qualitySelect = document.getElementById('qualitySelect');
        this.formatSelect = document.getElementById('formatSelect');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.infoBtn = document.getElementById('infoBtn');
        
        // X/Twitter interface elements
        this.xTwitterUsername = document.getElementById('xTwitterUsername');
        this.tweetCount = document.getElementById('tweetCount');
        this.searchTweetsBtn = document.getElementById('searchTweetsBtn');
        this.tweetsListCard = document.getElementById('tweetsListCard');
        this.tweetsList = document.getElementById('tweetsList');
        this.tweetConfigCard = document.getElementById('tweetConfigCard');
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
        
        // X/Twitter interface events
        this.searchTweetsBtn.addEventListener('click', () => this.searchTweets());
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
        
        this.xTwitterUsername.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchTweets();
        });
    }
    
    onPlatformChange() {
        const platform = this.platformSelect.value;
        this.log(`🎯 Plataforma selecionada: ${platform}`);
        
        // Apply platform theme to body
        this.applyPlatformTheme(platform);
        
        // Update platform indicator
        const indicators = {
            'Instagram': {
                text: '📷 Instagram: Download no formato original',
                class: 'platform-instagram',
                emoji: '📷'
            },
            'Facebook': {
                text: '📘 Facebook: Download no formato original',
                class: 'platform-facebook',
                emoji: '📘'
            },
            'TikTok': {
                text: '🎵 TikTok (requer login): Download no formato original',
                class: 'platform-tiktok',
                emoji: '🎵'
            },
            'X/Twitter': {
                text: '🐦 X/Twitter: Download no formato original',
                class: 'platform-twitter',
                emoji: '🐦'
            }
        };
        
        const indicator = indicators[platform];
        this.platformIndicator.textContent = `${indicator.emoji} ${indicator.text}`;
        this.platformIndicator.className = `platform-indicator ${indicator.class}`;
        
        // CORREÇÃO: Todas as plataformas usam a interface padrão
        // Remover lógica de interface especial para X/Twitter
        this.showStandardInterface();
        
        // Update options visibility
        this.updateOptionsVisibility(platform);
        
        // Log platform theme change
        this.log(`🎨 Tema ${platform} aplicado`);
    }
    
    applyPlatformTheme(platform) {
        // Remove all existing theme classes
        document.body.classList.remove(
            'theme-instagram', 
            'theme-facebook',
            'theme-tiktok',
            'theme-twitter'
        );
        
        // Apply new theme class
        const themeClass = `theme-${platform.toLowerCase()}`;
        document.body.classList.add(themeClass);
        
        // Update page title with platform emoji
        const platformEmojis = {
            'Instagram': '',
            'Facebook': '',
            'TikTok': '',
            'X/Twitter': ''
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
        this.xTwitterInterface.style.display = 'none';
        this.log(' Interface padrão ativada');
    }
    
    showXTwitterInterface() {
        this.standardInterface.style.display = 'none';
        this.xTwitterInterface.style.display = 'block';
        this.log(' Interface X/Twitter ativada');
    }
    
    updateOptionsVisibility(platform) {
        if (platform === 'Instagram') {
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
        
        // Validação simples por URL (sem endpoint backend)
        const platformPatterns = {
            'Instagram': /instagram\.com/i,
            'Facebook': /(facebook\.com|fb\.watch)/i,
            'TikTok': /tiktok\.com/i,
            'X/Twitter': /(twitter\.com|x\.com)/i
        };
        
        const pattern = platformPatterns[platform];
        if (pattern && pattern.test(url)) {
            this.log(`✅ URL ${platform} válida`);
            this.showAlert(`URL ${platform} válida`, 'success');
        } else {
            this.log(`❌ URL não é válida para ${platform}`);
            this.showAlert(`URL não é válida para ${platform}`, 'danger');
        }
    }

    async getVideoInfo() {
        const url = this.videoUrl.value.trim();
        const platform = this.platformSelect.value;
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        // Informações básicas sem endpoint backend
        this.log(`ℹ️ Informações básicas para ${platform}`);
        this.showAlert(`Plataforma: ${platform}. Use o botão Download para baixar o vídeo.`, 'info');
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
                if (platform === 'Instagram') {
                    this.log(` Qualidade: ${quality}`);
                    this.log(` Formato: ${format}`);
                }
                
                // AGUARDAR o download terminar usando polling
                this.log(' Aguardando download terminar...');
                this.updateProgress(25, 'processing');
                await this.waitForDownloadComplete(data.download_id);
                
                // Atualizar progresso para todos os ambientes (local e Vercel)
                this.log(' Download concluído com sucesso!');
                this.updateProgress(100, 'completed');
                this.downloadFileBtn.style.display = 'block';
                
                // Mostrar informações dos arquivos
                if (data.files && data.files.length > 0) {
                    data.files.forEach(file => {
                        this.log(` Arquivo: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
                    });
                }
            } else {
                // Melhorar tratamento de erro para evitar "undefined"
                const errorMessage = data.message || data.error || 'Erro desconhecido no download';
                this.log(` ${errorMessage}`);
                this.showAlert(errorMessage, 'danger');
                this.progressCard.style.display = 'none';
            }
        } catch (error) {
            // Melhorar tratamento de erro de rede/parsing
            const errorMessage = error.message || 'Erro de conexão ou resposta inválida';
            this.log(` Erro no download: ${errorMessage}`);
            this.showAlert(`Erro no download: ${errorMessage}`, 'danger');
            this.progressCard.style.display = 'none';
        } finally {
            this.setButtonLoading(this.downloadBtn, false);
        }
    }
    
    async searchTweets() {
        // X/Twitter search não implementado no backend atual
        this.showAlert('Funcionalidade X/Twitter em desenvolvimento. Use a interface padrão para URLs diretas.', 'info');
        this.log('⚠️ X/Twitter search não implementado - use interface padrão');
    }

    displayTweets(tweets) {
        // Função mantida para compatibilidade, mas não usada
        this.log('⚠️ displayTweets não implementado');
    }

    selectTweet(index) {
        // Função mantida para compatibilidade, mas não usada
        this.log('⚠️ selectTweet não implementado');
    }

    async downloadSegment() {
        // X/Twitter segment download não implementado no backend atual
        this.showAlert('Funcionalidade X/Twitter em desenvolvimento. Use a interface padrão para URLs diretas.', 'info');
        this.log('⚠️ X/Twitter segment download não implementado - use interface padrão');
    }

    downloadFile() {
        if (this.isVercel && this.downloadFiles && this.downloadFiles.length > 0) {
            // No Vercel, usar os arquivos da resposta HTTP
            const file = this.downloadFiles[0]; // Pegar o primeiro arquivo
            window.open(file.download_url, '_blank');
            this.log(`📥 Iniciando download: ${file.name}`);
        } else if (this.currentDownloadId) {
            // Usar endpoint correto /file/ em vez de /api/download_file/
            window.open(`/file/${this.currentDownloadId}`, '_blank');
            this.log('📥 Iniciando download do arquivo');
        }
    }
    
    async waitForDownloadComplete(downloadId) {
        const interval = 2000; // 2 segundos
        const timeout = 300000; // 5 minutos
        
        const startTime = Date.now();
        
        while (true) {
            const response = await fetch(`/status/${downloadId}`);
            const data = await response.json();
            
            if (data.status === 'completed') {
                break;
            } else if (data.status === 'error') {
                this.log(` Erro no download: ${data.error}`);
                this.showAlert(`Erro no download: ${data.error}`, 'danger');
                this.progressCard.style.display = 'none';
                return;
            }
            
            const elapsed = Date.now() - startTime;
            if (elapsed > timeout) {
                this.log(' Tempo limite excedido. Cancelando download...');
                this.showAlert('Tempo limite excedido. Cancelando download...', 'danger');
                this.progressCard.style.display = 'none';
                return;
            }
            
            await new Promise(resolve => setTimeout(resolve, interval));
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
            'Instagram': '',
            'Facebook': '',
            'TikTok': '',
            'X/Twitter': ''
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
