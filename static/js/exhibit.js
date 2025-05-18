// 获取DOM元素
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// 初始化聊天消息容器的滚动位置
chatMessages.scrollTop = chatMessages.scrollHeight;

// 添加消息到聊天窗口
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messagePara = document.createElement('p');
    messagePara.textContent = content;
    
    messageDiv.appendChild(messagePara);
    chatMessages.appendChild(messageDiv);
    
    // 滚动到最新消息
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 发送用户消息并获取AI回复
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // 显示用户消息
    addMessage(message, 'user');
    
    // 清空输入框
    userInput.value = '';
    
    try {
        // 显示加载状态
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message ai loading';
        loadingDiv.innerHTML = '<p>AI思考中...</p>';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 发送API请求
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                exhibit: exhibitName
            })
        });
        
        const data = await response.json();
        
        // 移除加载状态
        chatMessages.removeChild(loadingDiv);
        
        // 显示AI回复
        if (data.error) {
            addMessage(`抱歉，出现了错误：${data.error}`, 'ai');
        } else {
            addMessage(data.response, 'ai');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('抱歉，连接服务器时出现错误。请稍后再试。', 'ai');
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

// 展品卡片点击效果
const itemCards = document.querySelectorAll('.item-card');

itemCards.forEach(card => {
    card.addEventListener('click', function() {
        // 移除所有卡片的active类
        itemCards.forEach(c => c.classList.remove('active'));
        
        // 为当前点击的卡片添加active类
        this.classList.add('active');
        
        // 获取展品ID和名称
        const itemId = this.getAttribute('data-item-id');
        const itemName = this.querySelector('h4').textContent;
        
        // 可以在这里添加更多交互，例如显示详细信息等
        userInput.value = `请详细介绍一下${itemName}`;
        userInput.focus();
    });
}); 