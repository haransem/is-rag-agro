/**
 * Main Application JavaScript for Agriculture RAG System
 */

class RagApp {
    constructor() {
        this.currentTab = 'chat';
        this.conversations = new Map();
        this.currentConversationId = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkSystemStatus();
        this.loadConfigurations();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Chat functionality
        this.setupChatEventListeners();
        
        // Documents functionality
        this.setupDocumentEventListeners();
        
        // Search functionality
        this.setupSearchEventListeners();
        
        // Configuration functionality
        this.setupConfigEventListeners();
        
        // Status functionality
        this.setupStatusEventListeners();
    }

    setupChatEventListeners() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');

        // Send message on button click
        sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter (but not Shift+Enter)
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        });
    }

    setupDocumentEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const processFolderBtn = document.getElementById('processFolderBtn');
        const folderPath = document.getElementById('folderPath');

        // File upload
        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(Array.from(e.target.files));
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            this.handleFileUpload(files);
        });

        // Process folder
        processFolderBtn.addEventListener('click', () => {
            const path = folderPath.value.trim();
            if (path) {
                this.processFolder([path]);
            } else {
                this.showToast('กรุณาใส่พาธโฟลเดอร์', 'warning');
            }
        });

        // Folder buttons
        document.querySelectorAll('.folder-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const folderPath = e.target.dataset.folder;
                document.getElementById('folderPath').value = folderPath;
            });
        });
    }

    setupSearchEventListeners() {
        const searchButton = document.getElementById('searchButton');
        const searchInput = document.getElementById('searchInput');
        const similarityThreshold = document.getElementById('similarityThreshold');
        const thresholdValue = document.getElementById('thresholdValue');

        searchButton.addEventListener('click', () => this.performSearch());
        
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Update threshold value display
        similarityThreshold.addEventListener('input', (e) => {
            thresholdValue.textContent = parseFloat(e.target.value).toFixed(1);
        });
    }

    setupConfigEventListeners() {
        // Configuration will be set up dynamically when loaded
    }

    setupStatusEventListeners() {
        const refreshButton = document.getElementById('refreshStatus');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => this.loadSystemStatus());
        }
    }

    // Tab Management
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        this.currentTab = tabName;

        // Load content for specific tabs
        switch(tabName) {
            case 'config':
                this.loadConfigurations();
                break;
            case 'status':
                this.loadSystemStatus();
                break;
        }
    }

    // Chat Functionality
    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) return;

        const includeSources = document.getElementById('includeSources').checked;
        const debugMode = document.getElementById('debugMode').checked;

        // Clear input and disable send button
        chatInput.value = '';
        chatInput.style.height = 'auto';
        const sendButton = document.getElementById('sendButton');
        sendButton.disabled = true;

        // Add user message to chat
        this.addMessageToChat('user', message);

        try {
            // Show loading
            const loadingId = this.addMessageToChat('assistant', 'กำลังคิดคำตอบ... 🤔', { isLoading: true });

            // Send request
            const response = await api.askQuestion(message, {
                conversationId: this.currentConversationId,
                includeSources,
                debug: debugMode
            });

            // Remove loading message
            this.removeMessageFromChat(loadingId);

            // Add response to chat
            this.addMessageToChat('assistant', response.answer, {
                sources: response.sources,
                debug: response.debug_info,
                metadata: response.metadata
            });

            // Update conversation ID
            this.currentConversationId = response.conversation_id;

        } catch (error) {
            // Remove loading message
            this.removeMessageFromChat(loadingId);
            
            // Add error message
            this.addMessageToChat('assistant', `เกิดข้อผิดพลาด: ${error.message}`, { isError: true });
            this.showToast(`ไม่สามารถส่งข้อความได้: ${error.message}`, 'error');
        } finally {
            sendButton.disabled = false;
        }
    }

    addMessageToChat(sender, content, options = {}) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.id = messageId;

        let messageContent = `
            <div class="message-content">
                ${sender === 'assistant' ? '<i class="fas fa-robot"></i>' : ''}
                ${sender === 'user' ? '<i class="fas fa-user"></i>' : ''}
                <div>
                    <p>${content}</p>
                </div>
            </div>
        `;

        // Add sources if available
        if (options.sources && options.sources.length > 0) {
            const sourcesHtml = options.sources.map(source => `
                <div class="source-item">
                    <strong>คะแนน:</strong> ${(source.relevance_score || 0).toFixed(2)}<br>
                    <strong>เนื้อหา:</strong> ${source.content}<br>
                    <small><strong>แหล่งที่มา:</strong> ${source.metadata.source || 'ไม่ระบุ'}</small>
                </div>
            `).join('');

            messageContent += `
                <div class="message-sources">
                    <strong>🔍 แหล่งข้อมูลอ้างอิง:</strong>
                    ${sourcesHtml}
                </div>
            `;
        }

        // Add debug info if available
        if (options.debug) {
            messageContent += `
                <details style="margin-top: 10px; font-size: 0.8rem;">
                    <summary>🐛 ข้อมูล Debug</summary>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 5px; overflow-x: auto;">
${JSON.stringify(options.debug, null, 2)}
                    </pre>
                </details>
            `;
        }

        messageDiv.innerHTML = messageContent;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return messageId;
    }

    removeMessageFromChat(messageId) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            messageElement.remove();
        }
    }

    // Document Management
    async handleFileUpload(files) {
        const processImmediately = document.getElementById('processImmediately').checked;
        
        this.showLoading(`กำลังอัปโหลดไฟล์ ${files.length} ไฟล์...`);

        try {
            const uploadPromises = files.map(async (file) => {
                try {
                    const response = await api.uploadDocument(file, {
                        uploaded_at: new Date().toISOString()
                    }, processImmediately);
                    
                    return { success: true, file: file.name, response };
                } catch (error) {
                    return { success: false, file: file.name, error: error.message };
                }
            });

            const results = await Promise.all(uploadPromises);
            
            const successful = results.filter(r => r.success);
            const failed = results.filter(r => !r.success);

            let message = `อัปโหลดเสร็จสิ้น: สำเร็จ ${successful.length} ไฟล์`;
            if (failed.length > 0) {
                message += `, ล้มเหลว ${failed.length} ไฟล์`;
            }

            this.showToast(message, failed.length > 0 ? 'warning' : 'success');
            
            // Show detailed results
            this.showProcessingResults(results);

        } catch (error) {
            this.showToast(`ไม่สามารถอัปโหลดไฟล์ได้: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
            // Clear file input
            document.getElementById('fileInput').value = '';
        }
    }

    async processFolder(folderPaths) {
        this.showLoading('กำลังประมวลผลโฟลเดอร์...');

        try {
            const response = await api.processFolder(folderPaths);
            
            this.showToast(response.message, 'success');
            this.showProcessingResults([{
                success: true,
                type: 'folder',
                paths: folderPaths,
                response
            }]);

        } catch (error) {
            this.showToast(`ไม่สามารถประมวลผลโฟลเดอร์ได้: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showProcessingResults(results) {
        const statusDiv = document.getElementById('processingStatus');
        const contentDiv = document.getElementById('statusContent');
        
        const resultsHtml = results.map(result => {
            if (result.success) {
                return `
                    <div class="result-item success">
                        <i class="fas fa-check-circle"></i>
                        <strong>${result.file || 'โฟลเดอร์'}:</strong> ${result.response.message || 'สำเร็จ'}
                    </div>
                `;
            } else {
                return `
                    <div class="result-item error">
                        <i class="fas fa-times-circle"></i>
                        <strong>${result.file || 'โฟลเดอร์'}:</strong> ${result.error}
                    </div>
                `;
            }
        }).join('');

        contentDiv.innerHTML = `
            <div class="processing-results">
                <h4>ผลการประมวลผล</h4>
                ${resultsHtml}
            </div>
        `;

        statusDiv.style.display = 'block';

        // Hide after 10 seconds
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 10000);
    }

    // Search Functionality
    async performSearch() {
        const searchInput = document.getElementById('searchInput');
        const query = searchInput.value.trim();
        
        if (!query) {
            this.showToast('กรุณาใส่คำค้นหา', 'warning');
            return;
        }

        const limit = parseInt(document.getElementById('resultLimit').value);
        const similarityThreshold = parseFloat(document.getElementById('similarityThreshold').value);

        this.showLoading('กำลังค้นหา...');

        try {
            const response = await api.searchDocuments(query, {
                limit,
                similarityThreshold
            });

            this.displaySearchResults(response);

        } catch (error) {
            this.showToast(`การค้นหาล้มเหลว: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displaySearchResults(response) {
        const resultsDiv = document.getElementById('searchResults');
        
        if (response.results.length === 0) {
            resultsDiv.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>ไม่พบผลลัพธ์ที่ตรงกับคำค้นหา "${response.query}"</p>
                </div>
            `;
            return;
        }

        const resultsHtml = response.results.map(result => `
            <div class="search-result">
                <div class="search-result-header">
                    <h4>ผลลัพธ์การค้นหา</h4>
                    <span class="search-result-score">${(result.score * 100).toFixed(1)}%</span>
                </div>
                <div class="search-result-content">
                    ${result.content}
                </div>
                <div class="search-result-metadata">
                    <span><i class="fas fa-file"></i> ${result.metadata.source || 'ไม่ระบุแหล่งที่มา'}</span>
                    ${result.metadata.page ? `<span><i class="fas fa-file-alt"></i> หน้า ${result.metadata.page}</span>` : ''}
                    ${result.metadata.document_type ? `<span><i class="fas fa-tag"></i> ${result.metadata.document_type}</span>` : ''}
                </div>
            </div>
        `).join('');

        resultsDiv.innerHTML = `
            <div class="search-summary">
                <p>พบ ${response.total_results} ผลลัพธ์สำหรับ "<strong>${response.query}</strong>" 
                   ใช้เวลา ${(response.execution_time * 1000).toFixed(0)} มิลลิวินาที</p>
            </div>
            ${resultsHtml}
        `;
    }

    // Configuration Management
    async loadConfigurations() {
        if (this.currentTab !== 'config') return;

        const categories = ['database', 'models', 'processing'];
        
        for (const category of categories) {
            try {
                const config = await api.getConfig(category);
                this.renderConfigSection(category, config);
            } catch (error) {
                console.error(`Failed to load ${category} config:`, error);
                this.showConfigError(category, error.message);
            }
        }
    }

    renderConfigSection(category, config) {
        const sectionDiv = document.getElementById(`${category}Config`);
        
        const formFields = this.generateConfigForm(category, config.current_settings, config.available_options);
        
        sectionDiv.innerHTML = `
            <form class="config-form" data-category="${category}">
                ${formFields}
                <div class="config-actions">
                    <button type="submit" class="config-btn primary">
                        <i class="fas fa-save"></i> บันทึก
                    </button>
                    <button type="button" class="config-btn secondary" onclick="app.resetConfig('${category}')">
                        <i class="fas fa-undo"></i> รีเซ็ต
                    </button>
                </div>
            </form>
        `;

        // Add form submit handler
        const form = sectionDiv.querySelector('.config-form');
        form.addEventListener('submit', (e) => this.handleConfigSubmit(e));
    }

    generateConfigForm(category, settings, options) {
        const fields = [];

        for (const [key, value] of Object.entries(settings)) {
            let inputHtml = '';
            let description = this.getConfigDescription(category, key);

            if (options && options[`${key}_range`]) {
                // Range input
                const [min, max] = options[`${key}_range`];
                inputHtml = `
                    <input type="range" 
                           class="config-input" 
                           name="${key}" 
                           min="${min}" 
                           max="${max}" 
                           value="${value}">
                    <span class="range-value">${value}</span>
                `;
            } else if (options && options[`${key}_options`]) {
                // Select input
                const optionElements = options[`${key}_options`].map(opt => 
                    `<option value="${opt}" ${opt === value ? 'selected' : ''}>${opt}</option>`
                ).join('');
                inputHtml = `
                    <select class="config-select" name="${key}">
                        ${optionElements}
                    </select>
                `;
            } else if (Array.isArray(value)) {
                // Array input
                inputHtml = `
                    <input type="text" 
                           class="config-input" 
                           name="${key}" 
                           value="${value.join(', ')}"
                           placeholder="คั่นด้วยจุลภาค">
                `;
            } else if (typeof value === 'boolean') {
                // Checkbox input
                inputHtml = `
                    <input type="checkbox" 
                           class="config-input" 
                           name="${key}" 
                           ${value ? 'checked' : ''}>
                `;
            } else {
                // Text input
                inputHtml = `
                    <input type="text" 
                           class="config-input" 
                           name="${key}" 
                           value="${value}">
                `;
            }

            fields.push(`
                <div class="config-item">
                    <div class="config-label">
                        <div>${this.formatConfigLabel(key)}</div>
                        <div class="config-description">${description}</div>
                    </div>
                    <div class="config-control">
                        ${inputHtml}
                    </div>
                </div>
            `);
        }

        return fields.join('');
    }

    formatConfigLabel(key) {
        const labels = {
            'persist_directory': 'ไดเรกทอรีฐานข้อมูล',
            'collection_name': 'ชื่อ Collection',
            'embedding_model': 'โมเดล Embedding',
            'llm_model': 'โมเดล LLM',
            'retriever_k': 'จำนวนเอกสารที่ค้นหา',
            'temperature': 'Temperature',
            'max_tokens': 'จำนวน Token สูงสุด',
            'chunk_size': 'ขนาด Chunk',
            'chunk_overlap': 'ความเหลื่อมล้ำ Chunk',
            'max_file_size_mb': 'ขนาดไฟล์สูงสุด (MB)',
            'enable_ocr': 'เปิดใช้งาน OCR',
            'ocr_languages': 'ภาษาสำหรับ OCR'
        };
        return labels[key] || key;
    }

    getConfigDescription(category, key) {
        const descriptions = {
            'database': {
                'persist_directory': 'พาธสำหรับเก็บข้อมูลฐานข้อมูล',
                'collection_name': 'ชื่อของ collection ในฐานข้อมูล'
            },
            'models': {
                'embedding_model': 'โมเดลสำหรับสร้าง embeddings',
                'llm_model': 'โมเดลภาษาขนาดใหญ่สำหรับตอบคำถาม',
                'retriever_k': 'จำนวนเอกสารที่จะดึงมาใช้ในการตอบคำถาม',
                'temperature': 'ระดับความสร้างสรรค์ของคำตอบ (0.0-2.0)',
                'max_tokens': 'จำนวน token สูงสุดสำหรับคำตอบ'
            },
            'processing': {
                'chunk_size': 'ขนาดของข้อความแต่ละชิ้นที่แบ่งจากเอกสาร',
                'chunk_overlap': 'จำนวนตัวอักษรที่เหลื่อมล้ำระหว่างชิ้น',
                'max_file_size_mb': 'ขนาดไฟล์สูงสุดที่ยอมรับ',
                'enable_ocr': 'เปิดใช้งานการอ่านตัวอักษรจากรูปภาพ',
                'ocr_languages': 'ภาษาที่ใช้ในการ OCR'
            }
        };
        return descriptions[category]?.[key] || '';
    }

    async handleConfigSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const category = form.dataset.category;
        const formData = new FormData(form);
        const settings = {};

        for (const [key, value] of formData.entries()) {
            const input = form.querySelector(`[name="${key}"]`);
            
            if (input.type === 'checkbox') {
                settings[key] = input.checked;
            } else if (input.type === 'range' || input.type === 'number') {
                settings[key] = parseFloat(value);
            } else if (key.includes('languages') || key.includes('extensions')) {
                // Array fields
                settings[key] = value.split(',').map(s => s.trim()).filter(s => s);
            } else {
                settings[key] = value;
            }
        }

        try {
            this.showLoading('กำลังบันทึกการตั้งค่า...');
            
            await api.updateConfig(category, settings);
            
            this.showToast('บันทึกการตั้งค่าเรียบร้อยแล้ว', 'success');
            
            // Reload configuration
            setTimeout(() => this.loadConfigurations(), 500);

        } catch (error) {
            this.showToast(`ไม่สามารถบันทึกการตั้งค่าได้: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async resetConfig(category) {
        if (!confirm(`ต้องการรีเซ็ตการตั้งค่า ${category} กลับเป็นค่าเริ่มต้นหรือไม่?`)) {
            return;
        }

        try {
            this.showLoading('กำลังรีเซ็ตการตั้งค่า...');
            
            await api.resetConfig(category);
            
            this.showToast('รีเซ็ตการตั้งค่าเรียบร้อยแล้ว', 'success');
            
            // Reload configuration
            setTimeout(() => this.loadConfigurations(), 500);

        } catch (error) {
            this.showToast(`ไม่สามารถรีเซ็ตการตั้งค่าได้: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showConfigError(category, message) {
        const sectionDiv = document.getElementById(`${category}Config`);
        sectionDiv.innerHTML = `
            <div class="config-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>ไม่สามารถโหลดการตั้งค่าได้: ${message}</p>
                <button onclick="app.loadConfigurations()" class="config-btn secondary">
                    <i class="fas fa-retry"></i> ลองใหม่
                </button>
            </div>
        `;
    }

    // Status Management
    async loadSystemStatus() {
        if (this.currentTab !== 'status') return;

        try {
            const status = await api.getSystemStatus();
            this.renderSystemStatus(status);
        } catch (error) {
            console.error('Failed to load system status:', error);
            this.showStatusError(error.message);
        }
    }

    renderSystemStatus(status) {
        const statusGrid = document.getElementById('statusGrid');
        
        const cards = [];

        // Overall status card
        cards.push(`
            <div class="status-card ${status.status === 'healthy' ? '' : 'error'}">
                <div class="status-card-header">
                    <div class="status-card-title">
                        <i class="fas fa-heartbeat"></i>
                        สถานะรวม
                    </div>
                    <div class="status-card-value">${status.status === 'healthy' ? '✅' : '❌'}</div>
                </div>
                <div class="status-card-details">
                    สถานะ: ${status.status}<br>
                    อัปเดตล่าสุด: ${new Date(status.last_updated).toLocaleString('th-TH')}
                </div>
            </div>
        `);

        // Database status
        if (status.components.database) {
            const db = status.components.database;
            cards.push(`
                <div class="status-card">
                    <div class="status-card-header">
                        <div class="status-card-title">
                            <i class="fas fa-database"></i>
                            ฐานข้อมูล
                        </div>
                        <div class="status-card-value">${db.documents || 0}</div>
                    </div>
                    <div class="status-card-details">
                        สถานะ: ${db.status}<br>
                        เอกสาร: ${db.documents || 0} รายการ<br>
                        พาธ: ${db.path}
                    </div>
                </div>
            `);
        }

        // Models status
        if (status.components.models) {
            const models = status.components.models;
            cards.push(`
                <div class="status-card">
                    <div class="status-card-header">
                        <div class="status-card-title">
                            <i class="fas fa-brain"></i>
                            โมเดล AI
                        </div>
                        <div class="status-card-value">${models.available_models ? models.available_models.length : 0}</div>
                    </div>
                    <div class="status-card-details">
                        สถานะ: ${models.status}<br>
                        Embedding: ${models.embedding_model}<br>
                        LLM: ${models.llm_model}<br>
                        โมเดลที่มี: ${models.available_models ? models.available_models.length : 0} โมเดล
                    </div>
                </div>
            `);
        }

        // Processing status
        if (status.components.processing) {
            const processing = status.components.processing;
            cards.push(`
                <div class="status-card">
                    <div class="status-card-header">
                        <div class="status-card-title">
                            <i class="fas fa-cogs"></i>
                            การประมวลผล
                        </div>
                        <div class="status-card-value">${processing.supported_formats ? processing.supported_formats.length : 0}</div>
                    </div>
                    <div class="status-card-details">
                        สถานะ: ${processing.status}<br>
                        ขนาด Chunk: ${processing.chunk_size}<br>
                        ไฟล์ที่รองรับ: ${processing.supported_formats ? processing.supported_formats.length : 0} ประเภท
                    </div>
                </div>
            `);
        }

        // Statistics
        if (status.statistics) {
            const stats = status.statistics;
            cards.push(`
                <div class="status-card">
                    <div class="status-card-header">
                        <div class="status-card-title">
                            <i class="fas fa-chart-bar"></i>
                            สถิติ
                        </div>
                        <div class="status-card-value">${stats.total_documents || 0}</div>
                    </div>
                    <div class="status-card-details">
                        เอกสารทั้งหมด: ${stats.total_documents || 0}<br>
                        Uptime: ${stats.uptime || 'N/A'}<br>
                        คำถามล่าสุด: ${stats.last_query || 'ไม่มี'}
                    </div>
                </div>
            `);
        }

        statusGrid.innerHTML = cards.join('');
    }

    showStatusError(message) {
        const statusGrid = document.getElementById('statusGrid');
        statusGrid.innerHTML = `
            <div class="status-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>ไม่สามารถโหลดสถานะระบบได้: ${message}</p>
                <button onclick="app.loadSystemStatus()" class="refresh-btn">
                    <i class="fas fa-retry"></i> ลองใหม่
                </button>
            </div>
        `;
    }

    // System Status Check
    async checkSystemStatus() {
        try {
            const health = await api.getHealth();
            this.updateSystemStatusIndicator('healthy', 'ระบบทำงานปกติ');
        } catch (error) {
            this.updateSystemStatusIndicator('error', 'ระบบขัดข้อง');
            console.error('System health check failed:', error);
        }
    }

    updateSystemStatusIndicator(status, text) {
        const indicator = document.getElementById('statusIndicator');
        const statusText = document.querySelector('.status-text');
        
        indicator.className = `status-indicator ${status}`;
        statusText.textContent = text;
    }

    // UI Utilities
    showLoading(text = 'กำลังประมวลผล...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        
        loadingText.textContent = text;
        overlay.classList.add('show');
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('show');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);

        // Manual close on click
        toast.addEventListener('click', () => toast.remove());
    }

    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'times-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new RagApp();
});