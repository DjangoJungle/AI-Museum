// 获取DOM元素
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const userRoleSelect = document.getElementById('userRole');
const scenarioOptions = document.querySelectorAll('.scenario-option');
const startConnectionBtn = document.getElementById('startConnectionBtn');
const figure2Select = document.getElementById('figure2');
const topicInput = document.getElementById('topic');
const connectionResult = document.querySelector('.connection-result');
const connectionContent = document.querySelector('.connection-content');

// 初始化聊天消息容器的滚动位置
chatMessages.scrollTop = chatMessages.scrollHeight;

// 添加消息到聊天窗口
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    if (type === 'historical-figure') {
        // 历史人物消息带头像
        const avatarDiv = document.createElement('div');
        avatarDiv.className = `message-avatar figure-${figureName}`;
        messageDiv.appendChild(avatarDiv);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        const messagePara = document.createElement('p');
        messagePara.textContent = content;
        contentDiv.appendChild(messagePara);
        messageDiv.appendChild(contentDiv);
    } else {
        // 用户消息
        const messagePara = document.createElement('p');
        messagePara.textContent = content;
        messageDiv.appendChild(messagePara);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // 滚动到最新消息
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 发送用户消息并获取历史人物回复
async function sendMessage() {
    const message = userInput.value.trim();
    const userRole = userRoleSelect.value;
    
    if (!message) return;
    
    // 显示用户消息
    addMessage(message, 'user');
    
    // 清空输入框
    userInput.value = '';
    
    try {
        // 显示加载状态
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message historical-figure loading';
        const loadingAvatar = document.createElement('div');
        loadingAvatar.className = `message-avatar figure-${figureName}`;
        const loadingContent = document.createElement('div');
        loadingContent.className = 'message-content';
        loadingContent.innerHTML = '<p>思考中...</p>';
        loadingDiv.appendChild(loadingAvatar);
        loadingDiv.appendChild(loadingContent);
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 发送API请求
        const response = await fetch('/api/figure_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                figure_id: figureId,
                user_role: userRole
            })
        });
        
        const data = await response.json();
        
        // 移除加载状态
        chatMessages.removeChild(loadingDiv);
        
        // 显示历史人物回复
        if (data.error) {
            addMessage(`抱歉，出现了错误：${data.error}`, 'historical-figure');
        } else {
            addMessage(data.response, 'historical-figure');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('抱歉，连接服务器时出现错误。请稍后再试。', 'historical-figure');
    }
}

// 处理历史分岔口选择
async function handleScenarioOption(event) {
    const button = event.target;
    const title = button.getAttribute('data-title');
    const choice = button.getAttribute('data-choice');
    const scenarioCard = button.closest('.scenario-card');
    const responseDiv = scenarioCard.querySelector('.scenario-response');
    
    // 显示响应区域和加载状态
    responseDiv.style.display = 'block';
    responseDiv.innerHTML = '<div class="loading">思考中...</div>';
    
    try {
        // 发送API请求
        const response = await fetch('/api/scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                choice: choice,
                figure_id: figureId
            })
        });
        
        const data = await response.json();
        
        // 显示响应
        if (data.error) {
            responseDiv.innerHTML = `<p class="error">抱歉，出现了错误：${data.error}</p>`;
        } else {
            responseDiv.innerHTML = `
                <div class="scenario-figure-response">
                    <div class="message-avatar figure-${figureName}"></div>
                    <div class="response-content">
                        <p>${data.response}</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        responseDiv.innerHTML = '<p class="error">抱歉，连接服务器时出现错误。请稍后再试。</p>';
    }
}

// 处理时空连线
async function handleTimeConnection() {
    const figure2Id = figure2Select.value;
    const topic = topicInput.value.trim() || '文化交流';
    
    // 显示结果区域和加载状态
    connectionResult.style.display = 'block';
    connectionContent.innerHTML = '<div class="loading">生成对话中...</div>';
    
    try {
        // 发送API请求
        const response = await fetch('/api/time_connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                figure1_id: figureId,
                figure2_id: figure2Id,
                topic: topic
            })
        });
        
        const data = await response.json();
        
        // 显示响应
        if (data.error) {
            connectionContent.innerHTML = `<p class="error">抱歉，出现了错误：${data.error}</p>`;
        } else {
            // 创建对话容器
            const chatContainer = document.createElement('div');
            chatContainer.className = 'chat-dialogue-container';
            
            // 添加标题
            const title = document.createElement('h5');
            title.textContent = `关于"${topic}"的跨时空对话`;
            chatContainer.appendChild(title);
            
            // 解析对话内容
            const figure1Name = figureName;
            const figure2Name = figure2Select.options[figure2Select.selectedIndex].text.split(' ')[0];
            
            // 从响应中提取对话内容并分割成多个消息
            let dialogContent = data.response;
            
            // 将对话分割为消息数组
            const messages = [];
            
            // 使用正则表达式匹配"人名: 消息内容"的模式
            const regex = new RegExp(`(${figure1Name}|${figure2Name})[:：]\\s*([^]*?)(?=(${figure1Name}|${figure2Name})[:：]|$)`, 'g');
            let match;
            
            while ((match = regex.exec(dialogContent)) !== null) {
                const speaker = match[1];
                const content = match[2].trim();
                
                if (content) {
                    messages.push({
                        speaker: speaker,
                        content: content
                    });
                }
            }
            
            // 如果正则表达式没有匹配到任何对话，尝试使用简单的换行符分割
            if (messages.length === 0) {
                const lines = dialogContent.split('\n');
                for (const line of lines) {
                    const colonIndex = line.indexOf(':');
                    if (colonIndex > 0) {
                        const speaker = line.substring(0, colonIndex).trim();
                        const content = line.substring(colonIndex + 1).trim();
                        
                        if ([figure1Name, figure2Name].includes(speaker) && content) {
                            messages.push({
                                speaker: speaker,
                                content: content
                            });
                        }
                    }
                }
            }
            
            // 如果还是没有匹配到对话，显示原始内容
            if (messages.length === 0) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'time-dialog';
                messageDiv.innerHTML = `<div class="dialog-content">${dialogContent}</div>`;
                chatContainer.appendChild(messageDiv);
            } else {
                // 创建对话消息容器
                const dialogMessages = document.createElement('div');
                dialogMessages.className = 'chat-messages time-dialogue';
                
                // 添加每条消息
                for (const msg of messages) {
                    const messageDiv = document.createElement('div');
                    const isFigure1 = msg.speaker === figure1Name;
                    
                    messageDiv.className = `message historical-figure ${isFigure1 ? 'figure1' : 'figure2'}`;
                    
                    // 添加头像
                    const avatarDiv = document.createElement('div');
                    avatarDiv.className = `message-avatar figure-${msg.speaker}`;
                    messageDiv.appendChild(avatarDiv);
                    
                    // 添加消息内容
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    
                    // 添加说话者名称
                    const speakerNameDiv = document.createElement('div');
                    speakerNameDiv.className = 'speaker-name';
                    speakerNameDiv.textContent = msg.speaker;
                    contentDiv.appendChild(speakerNameDiv);
                    
                    // 添加消息文本
                    const contentPara = document.createElement('p');
                    contentPara.textContent = msg.content;
                    contentDiv.appendChild(contentPara);
                    
                    messageDiv.appendChild(contentDiv);
                    dialogMessages.appendChild(messageDiv);
                }
                
                chatContainer.appendChild(dialogMessages);
            }
            
            // 将对话容器添加到页面
            connectionContent.innerHTML = '';
            connectionContent.appendChild(chatContainer);
        }
    } catch (error) {
        console.error('Error:', error);
        connectionContent.innerHTML = '<p class="error">抱歉，连接服务器时出现错误。请稍后再试。</p>';
    }
}

// 点击发送按钮时发送消息
sendBtn.addEventListener('click', sendMessage);

// 按下Enter键时发送消息
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// 为历史分岔口选项添加点击事件
scenarioOptions.forEach(option => {
    option.addEventListener('click', handleScenarioOption);
});

// 为时空连线按钮添加点击事件
startConnectionBtn.addEventListener('click', handleTimeConnection);

// 角色选择变化时提示用户
userRoleSelect.addEventListener('change', () => {
    const selectedRole = userRoleSelect.options[userRoleSelect.selectedIndex].text;
    addMessage(`您已切换身份为: ${selectedRole}`, 'system');
}); 