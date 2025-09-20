/**
 * Student Study Assistant - Frontend Application
 * Handles file uploads, chat interactions, and UI animations
 */

class StudyAssistant {
    constructor() {
        this.uploadedFiles = new Map();
        this.isProcessing = false;
        this.currentConversationId = null;
        
        this.init();
    }
    
    init() {
        this.initializeElements();
        this.attachEventListeners();
        this.initializeAnimations();
    }
    
    initializeElements() {
        // File upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.fileList = document.getElementById('fileList');
        
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.questionInput = document.getElementById('questionInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.suggestions = document.getElementById('suggestions');
        
        // UI elements
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.loadingText = document.getElementById('loadingText');
        this.getStartedBtn = document.getElementById('getStartedBtn');
        this.mainApp = document.getElementById('main-app');
    }
    
    attachEventListeners() {
        // File upload events - prevent double triggering
        this.uploadBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.fileInput.click();
        });
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        // Add click to upload area but only if not clicking the button
        this.uploadArea.addEventListener('click', (e) => {
            if (e.target !== this.uploadBtn && !this.uploadBtn.contains(e.target)) {
                this.fileInput.click();
            }
        });
        
        // Chat events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Suggestion clicks
        this.suggestions.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion')) {
                this.questionInput.value = e.target.textContent;
                this.questionInput.focus();
            }
        });
        
        // Get started button
        this.getStartedBtn.addEventListener('click', () => {
            this.scrollToSection('main-app');
        });
        
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('href').substring(1);
                this.scrollToSection(target);
                this.updateActiveNavLink(link);
            });
        });
    }
    
    initializeAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);
        
        // Observe elements for scroll animations
        document.querySelectorAll('.upload-chat-section, .feature-card').forEach(el => {
            observer.observe(el);
        });
        
        // Stagger animation for feature cards
        setTimeout(() => {
            document.querySelectorAll('.feature-card').forEach((card, index) => {
                card.style.animationDelay = `${index * 0.2}s`;
            });
        }, 100);
    }
    
    // === FILE HANDLING ===
    
    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.processFiles(files);
        // Clear the input to allow selecting the same file again
        event.target.value = '';
    }
    
    handleDragOver(event) {
        event.preventDefault();
        this.uploadArea.classList.add('drag-over');
    }
    
    handleDragLeave(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('drag-over');
    }
    
    handleDrop(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('drag-over');
        
        const files = Array.from(event.dataTransfer.files);
        this.processFiles(files);
    }
    
    async processFiles(files) {
        // Filter valid files
        const validFiles = files.filter(file => {
            const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
            const validExtensions = ['.pdf', '.docx', '.txt', '.md'];
            const hasValidType = validTypes.includes(file.type);
            const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
            
            return (hasValidType || hasValidExtension) && file.size <= 50 * 1024 * 1024; // 50MB limit
        });
        
        if (validFiles.length === 0) {
            this.showToast('Please select valid files (PDF, DOCX, TXT, MD) under 50MB', 'error');
            return;
        }
        
        // Show loading
        this.showLoading('Processing documents...');
        
        try {
            for (const file of validFiles) {
                await this.uploadFile(file);
            }
            
            this.hideLoading();
            this.enableChat();
            this.showToast(`Successfully processed ${validFiles.length} document(s)`, 'success');
            
        } catch (error) {
            this.hideLoading();
            this.showToast('Error processing documents. Please try again.', 'error');
            console.error('Upload error:', error);
        }
    }
    
    async uploadFile(file) {
        const fileId = this.generateId();
        
        // Add to file list immediately
        this.addFileToList(file, fileId, 'processing');
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/v1/documents/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Store file info using the server's document ID
            this.uploadedFiles.set(fileId, {
                serverId: result.id,  // Store the actual server document ID
                id: result.id || fileId,
                name: file.name,
                size: file.size,
                type: file.type,
                status: 'ready',
                chunks: result.chunk_count || 0
            });
            
            // Update file list
            this.updateFileStatus(fileId, 'ready');
            
        } catch (error) {
            this.updateFileStatus(fileId, 'error');
            throw error;
        }
    }
    
    addFileToList(file, fileId, status) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.dataset.fileId = fileId;
        
        const fileIcon = this.getFileIcon(file.name);
        const fileSize = this.formatFileSize(file.size);
        
        fileItem.innerHTML = `
            <div class="file-icon">
                <i class="${fileIcon}"></i>
            </div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${fileSize}</div>
            </div>
            <div class="file-status ${status}">${this.getStatusText(status)}</div>
            <button class="remove-file" onclick="app.removeFile('${fileId}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        this.fileList.appendChild(fileItem);
    }
    
    updateFileStatus(fileId, status) {
        const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
        if (fileItem) {
            const statusElement = fileItem.querySelector('.file-status');
            statusElement.className = `file-status ${status}`;
            statusElement.textContent = this.getStatusText(status);
        }
    }
    
    removeFile(fileId) {
        this.uploadedFiles.delete(fileId);
        const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
        if (fileItem) {
            fileItem.style.animation = 'slideOutRight 0.3s ease-out forwards';
            setTimeout(() => fileItem.remove(), 300);
        }
        
        if (this.uploadedFiles.size === 0) {
            this.disableChat();
        }
    }
    
    // === CHAT FUNCTIONALITY ===
    
    async sendMessage() {
        const question = this.questionInput.value.trim();
        if (!question || this.isProcessing) return;
        
        this.isProcessing = true;
        this.addMessageToChat(question, 'user');
        this.questionInput.value = '';
        this.updateStatus('processing');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Get the actual server document IDs
            const documentIds = Array.from(this.uploadedFiles.values())
                .filter(file => file.serverId)
                .map(file => file.serverId);
            
            console.log('Sending question with document IDs:', documentIds);
            
            const response = await fetch('/api/v1/chat/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    document_ids: documentIds  // Send actual server document IDs
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Chat API Error:', errorText);
                throw new Error(`Chat error: ${response.statusText} - ${errorText}`);
            }
            
            const result = await response.json();
            console.log('Chat API Response:', result);
            
            this.hideTypingIndicator();
            
            // Check if we got a proper answer
            if (result.answer && !result.answer.includes("couldn't find relevant information")) {
                this.addMessageToChat(result.answer, 'ai', result.sources);
            } else {
                // Debug: show what documents we have
                const docCount = Array.from(this.uploadedFiles.values()).length;
                const debugMsg = `I couldn't find relevant information. Debug info: ${docCount} documents uploaded. Please try a different question or re-upload your document.`;
                this.addMessageToChat(debugMsg, 'ai');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessageToChat('Sorry, I encountered an error processing your question. Please try again.', 'ai');
            this.showToast('Error processing your question', 'error');
        }
        
        this.isProcessing = false;
        this.updateStatus('ready');
    }
    
    addMessageToChat(content, sender, sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'user' ? 
            '<div class="user-avatar"><i class="fas fa-user"></i></div>' :
            '<div class="ai-avatar"><i class="fas fa-robot"></i></div>';
        
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="message-sources">
                    <strong>Sources:</strong>
                    ${sources.map(source => `
                        <div class="source-item">
                            📄 ${source.document} (Page ${source.page || 'N/A'})
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        // Format the content properly for AI messages
        let formattedContent;
        if (sender === 'ai') {
            formattedContent = this.formatAIResponse(content);
        } else {
            formattedContent = `<p>${content}</p>`;
        }
        
        messageDiv.innerHTML = `
            ${avatar}
            <div class="message-content">
                ${formattedContent}
                ${sourcesHtml}
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatAIResponse(content) {
        /**
         * Convert backend-formatted text to proper HTML for display
         */
        if (!content) return '<p>No response</p>';
        
        // Split content into lines for processing
        const lines = content.split('\n');
        let html = '';
        let inBulletList = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Skip empty lines but add spacing
            if (!line) {
                if (inBulletList) {
                    html += '</ul>';
                    inBulletList = false;
                }
                html += '<div class="line-break"></div>';
                continue;
            }
            
            // Handle bold headings (**text**)
            if (line.startsWith('**') && line.endsWith('**')) {
                if (inBulletList) {
                    html += '</ul>';
                    inBulletList = false;
                }
                const headingText = line.slice(2, -2);
                html += `<h4 class="ai-heading">${headingText}</h4>`;
                continue;
            }
            
            // Handle bullet points (  - text)
            if (line.startsWith('-') || line.match(/^\s*-\s/)) {
                if (!inBulletList) {
                    html += '<ul class="ai-list">';
                    inBulletList = true;
                }
                const bulletText = line.replace(/^\s*-\s*/, '');
                html += `<li>${bulletText}</li>`;
                continue;
            }
            
            // Handle numbered items (1. text)
            if (line.match(/^\d+\.\s/)) {
                if (inBulletList) {
                    html += '</ul>';
                    inBulletList = false;
                }
                html += `<p class="ai-numbered">${line}</p>`;
                continue;
            }
            
            // Regular paragraph
            if (inBulletList) {
                html += '</ul>';
                inBulletList = false;
            }
            html += `<p class="ai-paragraph">${line}</p>`;
        }
        
        // Close any remaining bullet list
        if (inBulletList) {
            html += '</ul>';
        }
        
        return html || '<p>No content</p>';
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="ai-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typing = document.getElementById('typing-indicator');
        if (typing) {
            typing.remove();
        }
    }
    
    enableChat() {
        this.questionInput.disabled = false;
        this.sendBtn.disabled = false;
        this.questionInput.placeholder = "Ask me anything about your documents...";
        this.updateStatus('ready');
    }
    
    disableChat() {
        this.questionInput.disabled = true;
        this.sendBtn.disabled = true;
        this.questionInput.placeholder = "Upload documents to start asking questions...";
        this.updateStatus('waiting');
    }
    
    updateStatus(status) {
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        const statusText = this.statusIndicator.querySelector('.status-text');
        
        statusDot.className = `status-dot ${status}`;
        
        const statusMessages = {
            ready: 'Ready',
            processing: 'Processing...',
            waiting: 'Waiting for documents',
            error: 'Error'
        };
        
        statusText.textContent = statusMessages[status] || 'Unknown';
    }
    
    // === UTILITY FUNCTIONS ===
    
    showLoading(text = 'Loading...') {
        this.loadingText.textContent = text;
        this.loadingOverlay.classList.add('show');
    }
    
    hideLoading() {
        this.loadingOverlay.classList.remove('show');
    }
    
    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 90px;
            right: 20px;
            padding: 12px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            backdrop-filter: blur(20px);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
        `;
        
        const colors = {
            success: '#22c55e',
            error: '#ef4444',
            info: '#3b82f6'
        };
        
        if (colors[type]) {
            toast.style.borderColor = colors[type];
            toast.style.boxShadow = `0 10px 30px ${colors[type]}33`;
        }
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    updateActiveNavLink(activeLink) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        activeLink.classList.add('active');
    }
    
    getFileIcon(filename) {
        const extension = filename.toLowerCase().split('.').pop();
        const icons = {
            pdf: 'fas fa-file-pdf',
            docx: 'fas fa-file-word',
            txt: 'fas fa-file-alt',
            md: 'fas fa-file-code'
        };
        return icons[extension] || 'fas fa-file';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    getStatusText(status) {
        const statusTexts = {
            processing: 'Processing...',
            ready: 'Ready',
            error: 'Error'
        };
        return statusTexts[status] || status;
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
}

// Additional CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .toast {
        animation: slideInRight 0.3s ease-out !important;
    }
`;
document.head.appendChild(style);

// Initialize application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new StudyAssistant();
});