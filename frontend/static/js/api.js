/**
 * API Client for Agriculture RAG System
 */

class APIClient {
    constructor(baseURL = '/api/v1') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    /**
     * Make HTTP request
     */
    async request(method, endpoint, data = null, headers = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method,
            headers: { ...this.defaultHeaders, ...headers },
        };

        if (data) {
            if (data instanceof FormData) {
                delete config.headers['Content-Type'];
                config.body = data;
            } else {
                config.body = JSON.stringify(data);
            }
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ 
                    error: 'Unknown error',
                    message: `HTTP ${response.status}: ${response.statusText}` 
                }));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error(`API Error [${method} ${endpoint}]:`, error);
            throw error;
        }
    }

    // HTTP Methods
    async get(endpoint, headers = {}) {
        return this.request('GET', endpoint, null, headers);
    }

    async post(endpoint, data = null, headers = {}) {
        return this.request('POST', endpoint, data, headers);
    }

    async put(endpoint, data = null, headers = {}) {
        return this.request('PUT', endpoint, data, headers);
    }

    async delete(endpoint, headers = {}) {
        return this.request('DELETE', endpoint, null, headers);
    }

    // Chat API
    async askQuestion(question, options = {}) {
        const payload = {
            question,
            conversation_id: options.conversationId || null,
            include_sources: options.includeSources !== false,
            debug: options.debug || false
        };
        return this.post('/chat/ask', payload);
    }

    async getConversationHistory(conversationId) {
        return this.get(`/chat/conversations/${conversationId}`);
    }

    async deleteConversation(conversationId) {
        return this.delete(`/chat/conversations/${conversationId}`);
    }

    // Documents API
    async uploadDocument(file, metadata = {}, processImmediately = true) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('metadata', JSON.stringify(metadata));
        formData.append('process_immediately', processImmediately.toString());
        
        return this.post('/documents/upload', formData);
    }

    async processFolder(folderPaths) {
        return this.post('/documents/bulk-process', folderPaths);
    }

    async searchDocuments(query, options = {}) {
        const payload = {
            query,
            limit: options.limit || 10,
            similarity_threshold: options.similarityThreshold || 0.0,
            filters: options.filters || null
        };
        return this.post('/documents/search', payload);
    }

    async listDocuments() {
        return this.get('/documents/list');
    }

    async deleteDocument(documentId) {
        return this.delete(`/documents/${documentId}`);
    }

    async getDocumentInfo(documentId) {
        return this.get(`/documents/${documentId}/info`);
    }

    // Configuration API
    async getConfig(category) {
        return this.get(`/config/${category}`);
    }

    async getAllConfigs() {
        return this.get('/config/');
    }

    async updateConfig(category, settings) {
        const payload = {
            category,
            settings
        };
        return this.put(`/config/${category}`, payload);
    }

    async resetConfig(category) {
        return this.post(`/config/reset/${category}`);
    }

    // Status API
    async getSystemStatus() {
        return this.get('/status/');
    }

    async getHealth() {
        return this.get('/status/health');
    }

    async getAvailableModels() {
        return this.get('/status/models');
    }

    async getStatistics() {
        return this.get('/status/statistics');
    }

    async resetSystem(confirm = false) {
        const payload = { confirm };
        return this.post('/status/reset', payload);
    }
}

// Create global API client instance
window.api = new APIClient();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}