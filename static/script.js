// Chatbot UI Application
class ChatbotApp {
    constructor() {
        this.apiBase = localStorage.getItem('apiEndpoint') || 'http://localhost:8000/api';
        this.currentConversationId = null;
        this.maxHistory = parseInt(localStorage.getItem('maxHistory')) || 50;
        this.isLoading = false;
        this.quotaExceeded = false;
        this.testMode = localStorage.getItem('testMode') === 'true';
        
        this.initializeElements();
        this.attachEventListeners();
        this.checkAIStatus();
        this.loadConversations();
        this.updateQuotaStatus();
    }

    initializeElements() {
        // Form and input
        this.chatForm = document.getElementById('chatForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.charCount = document.getElementById('charCount');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        // Messages
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messages = document.getElementById('messages');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        
        // Sidebar
        this.sidebar = document.getElementById('sidebar');
        this.toggleSidebarBtn = document.getElementById('toggleSidebar');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.conversationsList = document.getElementById('conversationsList');
        this.gapAnalysisBtn = document.getElementById('gapAnalysisBtn');
        this.exportChatBtn = document.getElementById('exportChatBtn');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        
        // Header
        this.chatTitle = document.getElementById('chatTitle');
        
        // Status
        this.aiStatus = document.getElementById('aiStatus');
        this.quotaStatus = document.getElementById('quotaStatus');
        this.testModeIndicator = document.getElementById('testModeIndicator');
        
        // Gap Analysis
        this.gapAnalysisModal = document.getElementById('gapAnalysisModal');
        this.closeGapAnalysisBtn = document.getElementById('closeGapAnalysisBtn');
        
        // Settings
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettingsBtn = document.getElementById('closeSettingsBtn');
        this.apiEndpointInput = document.getElementById('apiEndpoint');
        this.maxHistoryInput = document.getElementById('maxHistory');
        this.testModeToggle = document.getElementById('testModeToggle');
        
        // Suggestions
        this.suggestionBtns = document.querySelectorAll('.suggestion-btn');
    }

    attachEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Character count
        this.messageInput.addEventListener('input', () => {
            this.charCount.textContent = this.messageInput.value.length;
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });

        // New chat
        this.newChatBtn.addEventListener('click', () => {
            this.startNewChat();
        });

        // Export chat
        this.exportChatBtn.addEventListener('click', () => {
            this.exportChat();
        });

        // Gap Analysis
        if (this.gapAnalysisBtn) {
            this.gapAnalysisBtn.addEventListener('click', () => {
                this.showGapAnalysis();
            });
        }

        if (this.closeGapAnalysisBtn) {
            this.closeGapAnalysisBtn.addEventListener('click', () => {
                this.gapAnalysisModal.classList.remove('active');
            });
        }

        // Export chat
        this.exportChatBtn.addEventListener('click', () => {
            this.exportChat();
        });

        // Clear chat
        this.clearChatBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear this conversation?')) {
                this.clearCurrentChat();
            }
        });

        // Toggle sidebar (mobile)
        this.toggleSidebarBtn.addEventListener('click', () => {
            this.sidebar.classList.toggle('open');
        });

        // Settings
        this.settingsBtn.addEventListener('click', () => {
            this.settingsModal.classList.add('active');
            this.apiEndpointInput.value = this.apiBase;
            this.maxHistoryInput.value = this.maxHistory;
            this.testModeToggle.checked = this.testMode;
        });

        this.closeSettingsBtn.addEventListener('click', () => {
            this.saveSettings();
            this.settingsModal.classList.remove('active');
        });

        // Close modal on outside click
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.saveSettings();
                this.settingsModal.classList.remove('active');
            }
        });

        // Test mode toggle
        if (this.testModeToggle) {
            this.testModeToggle.addEventListener('change', () => {
                this.toggleTestMode();
            });
        }

        // Test mode toggle
        this.testModeToggle.addEventListener('change', () => {
            this.toggleTestMode();
        });

        // Suggestion buttons
        this.suggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const suggestion = btn.getAttribute('data-suggestion');
                this.messageInput.value = suggestion;
                this.charCount.textContent = suggestion.length;
                this.messageInput.focus();
                this.sendMessage();
            });
        });

        // Enter to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!this.isLoading) {
                    this.sendMessage();
                }
            }
        });
    }

    async checkAIStatus() {
        try {
            const response = await fetch(`${this.apiBase}/ai/info`);
            const data = await response.json();
            
            if (data.success) {
                this.updateAIStatus(true);
            } else {
                this.updateAIStatus(false);
            }
        } catch (error) {
            console.error('Error checking AI status:', error);
            this.updateAIStatus(false);
        }
    }

    updateAIStatus(isReady) {
        const statusIcon = this.aiStatus.querySelector('i');
        const statusText = this.aiStatus.querySelector('span');
        
        if (isReady) {
            statusIcon.style.color = 'var(--success-color)';
            statusText.textContent = 'AI Ready';
        } else {
            statusIcon.style.color = 'var(--error-color)';
            statusText.textContent = 'AI Offline';
        }
    }

    updateQuotaStatus() {
        if (this.quotaStatus) {
            if (this.quotaExceeded) {
                this.quotaStatus.style.display = 'flex';
                if (this.aiStatus) this.aiStatus.style.display = 'none';
            } else {
                this.quotaStatus.style.display = 'none';
                if (this.aiStatus) this.aiStatus.style.display = 'flex';
            }
        }

        if (this.testModeIndicator) {
            if (this.testMode) {
                this.testModeIndicator.style.display = 'flex';
            } else {
                this.testModeIndicator.style.display = 'none';
            }
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isLoading) {
            return;
        }

        // Hide welcome screen
        this.welcomeScreen.classList.add('hidden');
        
        // Add user message to UI
        this.addMessage('user', message);
        
        // Clear input
        this.messageInput.value = '';
        this.charCount.textContent = '0';
        this.messageInput.style.height = 'auto';
        
        // Check if test mode is active
        if (this.testMode) {
            this.setLoading(true);
            // Simulate API delay
            setTimeout(() => {
                const testResponse = this.getTestModeResponse(message);
                this.addMessage('ai', testResponse);
                this.setLoading(false);
            }, 1000);
            return;
        }
        
        // Show typing indicator
        this.setLoading(true);
        
        try {
            // Get chat history for context
            const chatHistory = this.getChatHistory();
            
            // Prepare request
            const requestBody = {
                message: message,
                conversation_id: this.currentConversationId,
                chat_history: chatHistory
            };

            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            // Check response status before parsing JSON
            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    errorData = { message: `HTTP ${response.status}: ${response.statusText}` };
                }
                
                // Handle quota/rate limit errors (429 status)
                if (response.status === 429) {
                    const errorMsg = errorData.message || errorData.detail || 'API quota exceeded';
                    throw new Error(errorMsg);
                }
                
                // Handle other HTTP errors
                throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success || data.response) {
                const aiResponse = data.response || data.data?.response || 'Sorry, I could not generate a response.';
                const conversationId = data.conversation_id || data.data?.conversation_id;
                
                // Update conversation ID
                if (conversationId && !this.currentConversationId) {
                    this.currentConversationId = conversationId;
                    this.chatTitle.textContent = 'Conversation';
                    this.loadConversations();
                }
                
                // Add AI response
                this.addMessage('ai', aiResponse);
            } else {
                throw new Error(data.message || 'Failed to get response');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = error.message || String(error) || 'Unknown error occurred';
            const errorStr = errorMessage.toLowerCase();
            
            // Handle quota exceeded errors with special message
            if (errorStr.includes('quota') || errorStr.includes('429') || errorStr.includes('limit') || 
                errorStr.includes('exceeded') || errorStr.includes('too many requests')) {
                this.quotaExceeded = true;
                this.updateQuotaStatus();
                
                // Offer test mode if quota exceeded
                if (!this.testMode) {
                    this.addMessage('ai', 
                        '⚠️ API Quota Exceeded\n\n' +
                        'Your free tier API quota has been reached.\n\n' +
                        '**Options:**\n' +
                        '• Wait 30-60 minutes for quota reset\n' +
                        '• Check usage: https://ai.dev/usage\n' +
                        '• Upgrade plan: https://ai.google.dev/pricing\n' +
                        '• Enable Test Mode (simulated responses)\n\n' +
                        'Click the settings icon ⚙️ to enable Test Mode for testing without API calls.'
                    );
                } else {
                    // Test mode is active, use fallback response
                    this.addMessage('ai', this.getTestModeResponse(message));
                    return;
                }
                this.showError('API quota exceeded. Test Mode available in settings.', 'warning');
            } else if (errorStr.includes('network') || errorStr.includes('fetch') || errorStr.includes('failed to fetch')) {
                this.addMessage('ai', '❌ Network Error\n\nPlease check your internet connection and try again.');
                this.showError('Network error. Please check your connection.');
            } else {
                this.addMessage('ai', `Sorry, I encountered an error: ${errorMessage}`);
                this.showError(`Error: ${errorMessage}`);
            }
        } finally {
            this.setLoading(false);
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' 
            ? '<i class="fas fa-user"></i>' 
            : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = content;
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageContent.appendChild(bubble);
        messageContent.appendChild(time);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    getChatHistory() {
        const messageElements = this.messages.querySelectorAll('.message');
        const history = [];
        
        messageElements.forEach(msg => {
            const role = msg.classList.contains('user') ? 'user' : 'assistant';
            const content = msg.querySelector('.message-bubble').textContent;
            history.push({
                role: role,
                content: content
            });
        });
        
        return history.slice(-this.maxHistory);
    }

    setLoading(loading) {
        this.isLoading = loading;
        this.sendBtn.disabled = loading;
        this.messageInput.disabled = loading;
        
        if (loading) {
            this.typingIndicator.style.display = 'flex';
        } else {
            this.typingIndicator.style.display = 'none';
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    startNewChat() {
        this.currentConversationId = null;
        this.messages.innerHTML = '';
        this.welcomeScreen.classList.remove('hidden');
        this.chatTitle.textContent = 'New Conversation';
        this.messageInput.focus();
    }

    async clearCurrentChat() {
        if (this.currentConversationId) {
            try {
                await fetch(`${this.apiBase}/chat/conversations/${this.currentConversationId}`, {
                    method: 'DELETE'
                });
            } catch (error) {
                console.error('Error deleting conversation:', error);
            }
        }
        this.startNewChat();
        this.loadConversations();
    }

    async loadConversations() {
        try {
            const response = await fetch(`${this.apiBase}/chat/conversations?limit=10`);
            const data = await response.json();
            
            if (data.success && data.data) {
                this.renderConversations(data.data);
            } else {
                this.conversationsList.innerHTML = '<div class="loading">No conversations yet</div>';
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.conversationsList.innerHTML = '<div class="loading">Error loading conversations</div>';
        }
    }

    renderConversations(conversations) {
        if (conversations.length === 0) {
            this.conversationsList.innerHTML = '<div class="loading">No conversations yet</div>';
            return;
        }

        this.conversationsList.innerHTML = conversations.map(conv => {
            const firstMessage = conv.first_message || 'New conversation';
            const messageCount = conv.message_count || 0;
            const date = conv.updated_at ? new Date(conv.updated_at).toLocaleDateString() : '';
            
            return `
                <div class="conversation-item ${conv.conversation_id === this.currentConversationId ? 'active' : ''}" 
                     data-id="${conv.conversation_id}">
                    <div class="icon"><i class="fas fa-comment"></i></div>
                    <div class="content">
                        <div class="title">${this.truncateText(firstMessage, 30)}</div>
                        <div class="meta">${messageCount} messages • ${date}</div>
                    </div>
                </div>
            `;
        }).join('');

        // Attach click listeners
        this.conversationsList.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => {
                const conversationId = item.getAttribute('data-id');
                this.loadConversation(conversationId);
            });
        });
    }

    async loadConversation(conversationId) {
        try {
            const response = await fetch(`${this.apiBase}/chat/history/${conversationId}?limit=${this.maxHistory}`);
            const data = await response.json();
            
            if (data.success && data.data) {
                this.currentConversationId = conversationId;
                this.messages.innerHTML = '';
                this.welcomeScreen.classList.add('hidden');
                this.chatTitle.textContent = 'Conversation';
                
                const messages = data.data.messages || [];
                messages.forEach(msg => {
                    this.addMessage(msg.role, msg.content);
                });
                
                this.loadConversations(); // Refresh list to update active state
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
            this.showError('Failed to load conversation');
        }
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    showError(message, type = 'error') {
        // Enhanced error notification with types
        const errorDiv = document.createElement('div');
        let bgColor = 'var(--error-color)';
        let icon = '❌';
        
        if (type === 'warning') {
            bgColor = 'var(--warning-color)';
            icon = '⚠️';
        } else if (type === 'info') {
            bgColor = 'var(--info-color)';
            icon = 'ℹ️';
        }
        
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: var(--shadow-lg);
            z-index: 2000;
            animation: fadeIn 0.3s ease;
            max-width: 400px;
            line-height: 1.5;
        `;
        errorDiv.innerHTML = `<strong>${icon}</strong> ${message}`;
        document.body.appendChild(errorDiv);
        
        // Show longer for quota errors
        const duration = type === 'warning' ? 10000 : 5000;
        setTimeout(() => {
            errorDiv.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => errorDiv.remove(), 300);
        }, duration);
    }

    saveSettings() {
        this.apiBase = this.apiEndpointInput.value || 'http://localhost:8000/api';
        this.maxHistory = parseInt(this.maxHistoryInput.value) || 50;
        if (this.testModeToggle) {
            this.testMode = this.testModeToggle.checked;
        }
        
        localStorage.setItem('apiEndpoint', this.apiBase);
        localStorage.setItem('maxHistory', this.maxHistory.toString());
        localStorage.setItem('testMode', this.testMode.toString());
        
        this.updateQuotaStatus();
        
        // Recheck status with new endpoint
        this.checkAIStatus();
    }

    getTestModeResponse(userMessage) {
        // Fallback/test mode responses when quota is exceeded
        const message = userMessage.toLowerCase();
        
        // Greeting responses
        if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
            return 'Hello! 👋 I\'m in Test Mode (API quota exceeded). I can still help you test the chatbot interface!';
        }
        
        // Question responses
        if (message.includes('what') || message.includes('how') || message.includes('why')) {
            return 'That\'s a great question! In Test Mode, I provide simulated responses. Once your API quota resets, I\'ll be able to give you real AI-powered answers.';
        }
        
        // Help requests
        if (message.includes('help') || message.includes('support')) {
            return 'I\'m here to help! Currently in Test Mode due to API quota limits. You can:\n\n' +
                   '• Wait for quota reset (30-60 minutes)\n' +
                   '• Check usage: https://ai.dev/usage\n' +
                   '• Upgrade your plan for higher limits\n\n' +
                   'The chatbot interface is working perfectly - just waiting for API access!';
        }
        
        // Default test response
        return `[Test Mode Response]\n\nI received your message: "${userMessage}"\n\n` +
               'This is a simulated response because the API quota has been exceeded. ' +
               'Once your quota resets, you\'ll get real AI-powered responses!\n\n' +
               'The chatbot is fully functional - just needs API access to generate responses.';
    }

    toggleTestMode() {
        this.testMode = !this.testMode;
        localStorage.setItem('testMode', this.testMode.toString());
        this.updateQuotaStatus();
        
        if (this.testMode) {
            this.showError('Test Mode enabled - Using simulated responses', 'info');
            this.addMessage('ai', '🧪 Test Mode Enabled\n\nI\'ll now provide simulated responses for testing. Disable Test Mode in settings to use the real API.');
        } else {
            this.showError('Test Mode disabled - Using real API', 'info');
        }
    }

    exportChat() {
        const messages = this.messages.querySelectorAll('.message');
        if (messages.length === 0) {
            this.showError('No messages to export');
            return;
        }

        let exportText = `Chatbot Conversation Export\n`;
        exportText += `Generated: ${new Date().toLocaleString()}\n`;
        exportText += `Conversation ID: ${this.currentConversationId || 'N/A'}\n`;
        exportText += `${'='.repeat(50)}\n\n`;

        messages.forEach(msg => {
            const role = msg.classList.contains('user') ? 'User' : 'Assistant';
            const content = msg.querySelector('.message-bubble').textContent;
            const time = msg.querySelector('.message-time').textContent;
            exportText += `[${time}] ${role}:\n${content}\n\n`;
        });

        // Create download
        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chatbot-conversation-${this.currentConversationId || Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showError('Chat exported successfully!', 'info');
    }

    async showGapAnalysis() {
        if (!this.currentConversationId) {
            this.showError('Please start a conversation first', 'warning');
            return;
        }

        this.gapAnalysisModal.classList.add('active');
        const content = document.getElementById('gapAnalysisContent');
        content.innerHTML = '<div class="loading">Analyzing conversation...</div>';

        try {
            const response = await fetch(`${this.apiBase}/gap-analysis/conversation/${this.currentConversationId}`);
            const data = await response.json();

            if (data.success && data.data) {
                const analysis = data.data;
                this.renderGapAnalysis(analysis, content);
            } else {
                content.innerHTML = `<div class="error">Failed to analyze conversation: ${data.message || 'Unknown error'}</div>`;
            }
        } catch (error) {
            console.error('Error analyzing conversation:', error);
            content.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    }

    renderGapAnalysis(analysis, container) {
        const { gaps, suggestions, completeness_score, metrics, severity_breakdown } = analysis;

        let html = `
            <div class="gap-analysis">
                <div class="gap-score">
                    <h3>Completeness Score</h3>
                    <div class="score-circle" style="--score: ${completeness_score}">
                        <span>${completeness_score}%</span>
                    </div>
                </div>

                <div class="gap-metrics">
                    <h3>Conversation Metrics</h3>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <span class="metric-label">Total Messages</span>
                            <span class="metric-value">${metrics.total_messages}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">User Messages</span>
                            <span class="metric-value">${metrics.user_messages}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">AI Messages</span>
                            <span class="metric-value">${metrics.ai_messages}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Questions Asked</span>
                            <span class="metric-value">${metrics.questions_asked}</span>
                        </div>
                    </div>
                </div>

                <div class="gap-summary">
                    <h3>Gap Summary</h3>
                    <div class="severity-breakdown">
                        <span class="severity-badge high">High: ${severity_breakdown.high}</span>
                        <span class="severity-badge medium">Medium: ${severity_breakdown.medium}</span>
                        <span class="severity-badge low">Low: ${severity_breakdown.low}</span>
                    </div>
                </div>
        `;

        if (gaps && gaps.length > 0) {
            html += `
                <div class="gaps-list">
                    <h3>Identified Gaps (${gaps.length})</h3>
                    ${gaps.map(gap => `
                        <div class="gap-item severity-${gap.severity}">
                            <div class="gap-header">
                                <span class="gap-type">${gap.type.replace('_', ' ').toUpperCase()}</span>
                                <span class="gap-severity">${gap.severity}</span>
                            </div>
                            <p class="gap-description">${gap.description}</p>
                            <p class="gap-suggestion"><strong>Suggestion:</strong> ${gap.suggestion}</p>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            html += `
                <div class="no-gaps">
                    <i class="fas fa-check-circle"></i>
                    <p>No significant gaps identified! Conversation appears complete.</p>
                </div>
            `;
        }

        if (suggestions && suggestions.length > 0) {
            html += `
                <div class="suggestions-list">
                    <h3>Suggestions</h3>
                    <ul>
                        ${suggestions.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatbotApp = new ChatbotApp();
});

