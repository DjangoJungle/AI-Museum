from flask import Flask, render_template, request, jsonify, session
import os
import json
from dotenv import load_dotenv
import random

# 使用Together AI的直接接口
import together
from langchain_core.messages import HumanMessage, AIMessage

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)

# 配置Together API
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
together.api_key = TOGETHER_API_KEY

# 对话历史记录管理
conversation_histories = {}

# 历史人物角色数据
historical_figures = {
    "bronze_ding": {
        "name": "周武王",
        "era": "商周时期",
        "title": "周朝开国君主",
        "personality": "坚毅果断，崇尚礼制",
        "greeting": "吾乃周武王姬发，率诸侯伐纣，建立周朝之君。今日得见贵客，甚是欣慰。",
        "background": "周武王是西周的创建者，在牧野之战中击败商纣王，建立了周朝。他推行分封制，确立了周朝的礼乐制度。"
    },
    "terracotta_warriors": {
        "name": "秦始皇",
        "era": "秦朝",
        "title": "中国历史上第一位皇帝",
        "personality": "雄才大略，严厉果断",
        "greeting": "寡人乃秦始皇嬴政，统一六国，建立大秦帝国。你从何处而来，有何见教？",
        "background": "秦始皇统一六国，建立中国历史上第一个中央集权制国家，实行郡县制、书同文、车同轨等一系列重大改革。"
    },
    "porcelain_vase": {
        "name": "景德镇工匠",
        "era": "明朝",
        "title": "御窑厂首席工匠",
        "personality": "精益求精，温和内敛",
        "greeting": "在下乃景德镇御窑厂工匠，专为皇家烧造瓷器。这青花瓷器，乃是我等倾注心血之作。",
        "background": "明朝景德镇是世界瓷都，其青花瓷器工艺精湛，远销海外，成为中国文化的重要象征。"
    },
    "abstract_painting": {
        "name": "毕加索",
        "era": "20世纪",
        "title": "立体主义创始人",
        "personality": "前卫大胆，富有想象力",
        "greeting": "你好，我是巴勃罗·毕加索。艺术不是真理，艺术是谎言，让我们认识真理。",
        "background": "毕加索是20世纪最具影响力的艺术家之一，立体主义的创始人，其作品《格尔尼卡》等对现代艺术产生深远影响。"
    },
    "installation": {
        "name": "草间弥生",
        "era": "当代",
        "title": "前卫艺术家",
        "personality": "独特前卫，充满想象",
        "greeting": "欢迎来到我的无限世界。我是草间弥生，通过艺术，我试图表达宇宙的无限与人类存在的意义。",
        "background": "草间弥生是日本著名艺术家，以其独特的波点艺术和沉浸式装置作品闻名于世，被誉为'波点女王'。"
    },
    "digital_art": {
        "name": "数字艺术家",
        "era": "21世纪",
        "title": "NFT艺术先驱",
        "personality": "创新开放，热爱技术",
        "greeting": "嗨！欢迎来到数字艺术的世界。我们正在用代码和算法创造前所未有的艺术体验。",
        "background": "数字艺术是21世纪兴起的新艺术形式，结合了技术与创意，NFT技术的出现更是为数字艺术带来了新的可能性。"
    },
    "dinosaur_fossil": {
        "name": "古生物学家",
        "era": "现代",
        "title": "恐龙研究专家",
        "personality": "严谨求实，充满好奇",
        "greeting": "你好，我是研究侏罗纪恐龙化石的古生物学家。这些远古生物的奥秘，正等待我们去发现。",
        "background": "古生物学家通过研究化石，重建远古生物的形态和生活环境，帮助人类了解地球生命演化的历史。"
    },
    "minerals": {
        "name": "地质学家",
        "era": "现代",
        "title": "矿物研究专家",
        "personality": "细致观察，理性分析",
        "greeting": "欢迎来到矿物的奇妙世界。这些晶体结构展示了大自然的精密设计和数学美。",
        "background": "地质学家研究地球的物质组成、结构和历史，矿物学是地质学的重要分支，研究自然界中的矿物成分和特性。"
    },
    "ecosystem_model": {
        "name": "生态学家",
        "era": "现代",
        "title": "生态系统研究专家",
        "personality": "关注自然，热爱生命",
        "greeting": "你好，我是生态学家。生态系统是一个复杂而精妙的网络，每个物种都在其中扮演着重要角色。",
        "background": "生态学家研究生物与环境之间的关系，以及不同生物之间的相互作用，为保护生物多样性和可持续发展提供科学依据。"
    }
}

# 用户角色选项
user_roles = [
    {"id": "tourist", "name": "现代游客", "description": "对历史文化有兴趣的普通游客"},
    {"id": "scholar", "name": "历史学者", "description": "专业研究历史文化的学者"},
    {"id": "time_traveler", "name": "时空旅行者", "description": "来自未来的时空旅行者"},
    {"id": "emperor", "name": "古代帝王", "description": "拥有至高权力的古代统治者"},
    {"id": "merchant", "name": "古代商人", "description": "往来各国的贸易商人"}
]

# 博物馆展品数据 - 修改键名避免与Python内置方法冲突
museum_exhibits = {
    "ancient_china": {
        "name": "中国古代文明",
        "description": "展示了从新石器时代到明清时期的中国历史文物。",
        "exhibit_items": [
            {"id": "bronze_ding", "name": "青铜鼎", "era": "商周时期", "description": "古代礼器，象征权力与地位。"},
            {"id": "terracotta_warriors", "name": "兵马俑", "era": "秦朝", "description": "秦始皇陵墓的陪葬品，展示了秦朝军队的风貌。"},
            {"id": "porcelain_vase", "name": "青花瓷瓶", "era": "明朝", "description": "精美的青花瓷器，代表了中国陶瓷艺术的巅峰。"}
        ]
    },
    "modern_art": {
        "name": "现代艺术",
        "description": "20世纪以来的现代艺术作品展示。",
        "exhibit_items": [
            {"id": "abstract_painting", "name": "抽象画作", "era": "20世纪", "description": "探索形式、色彩与情感表达的现代艺术作品。"},
            {"id": "installation", "name": "装置艺术", "era": "当代", "description": "融合多种媒介的空间艺术表达。"},
            {"id": "digital_art", "name": "数字艺术", "era": "21世纪", "description": "利用数字技术创作的前沿艺术形式。"}
        ]
    },
    "natural_history": {
        "name": "自然历史",
        "description": "展示地球生命演化和自然奇观。",
        "exhibit_items": [
            {"id": "dinosaur_fossil", "name": "恐龙化石", "era": "侏罗纪", "description": "展示了远古生物的骨骼结构和生活环境。"},
            {"id": "minerals", "name": "矿物晶体", "era": "地质年代", "description": "各种罕见矿物的晶体结构展示。"},
            {"id": "ecosystem_model", "name": "生态系统模型", "era": "现代", "description": "展示不同生态环境中生物多样性的互动关系。"}
        ]
    }
}

# 历史事件和分岔口
historical_scenarios = {
    "terracotta_warriors": [
        {
            "title": "焚书坑儒的抉择",
            "description": "如果秦始皇没有焚书坑儒，而是广纳百家之言，历史会如何发展？",
            "options": ["支持百家争鸣", "仍然统一思想"]
        },
        {
            "title": "秦朝的继承",
            "description": "如果秦始皇选择了更有能力的继承人而非胡亥，秦朝是否能够延续？",
            "options": ["选择贤能继承", "仍由胡亥继位"]
        }
    ],
    "bronze_ding": [
        {
            "title": "周朝分封制的变革",
            "description": "如果周朝采取中央集权而非分封制，中国古代历史将如何改写？",
            "options": ["实行中央集权", "坚持分封制度"]
        }
    ],
    "abstract_painting": [
        {
            "title": "艺术与科技的融合",
            "description": "如果20世纪初期艺术与科技深度融合，现代艺术会呈现怎样的面貌？",
            "options": ["科技主导艺术", "艺术引领科技"]
        }
    ]
}

# 调用Together API的函数
def call_together_api(prompt, conversation_id=None):
    try:
        # 初始化对话历史
        if conversation_id not in conversation_histories:
            conversation_histories[conversation_id] = []
        
        # 获取当前对话历史
        history = conversation_histories[conversation_id]
        
        # 构建完整提示文本
        full_prompt = ""
        for msg in history:
            if isinstance(msg, HumanMessage):
                full_prompt += f"用户: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                full_prompt += f"助手: {msg.content}\n"
        
        # 添加当前问题
        full_prompt += f"用户: {prompt}\n助手: "
        
        print(f"发送提示: {full_prompt[:100]}...")
        
        # 调用Together API
        response = together.Complete.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            prompt=full_prompt,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
            top_k=40
        )
        
        print(f"API响应: {response}")
        
        # 获取回复内容 - 根据Together API的实际返回格式调整
        if isinstance(response, dict):
            if 'output' in response and 'content' in response['output']:
                ai_message = response['output']['content']
            elif 'choices' in response and len(response['choices']) > 0:
                ai_message = response['choices'][0]['text']
            elif 'generations' in response and len(response['generations']) > 0:
                ai_message = response['generations'][0]['text']
            else:
                # 尝试直接获取响应文本
                ai_message = str(response)
        else:
            # 如果不是字典类型，直接转为字符串
            ai_message = str(response)
        
        # 更新历史记录
        history.append(HumanMessage(content=prompt))
        history.append(AIMessage(content=ai_message))
        
        # 限制历史长度，避免token过多
        if len(history) > 10:
            # 保留最近的10条消息
            history = history[-10:]
        
        # 更新历史记录
        conversation_histories[conversation_id] = history
        
        return {
            "answer": ai_message,
            "conversation_id": conversation_id or f"conv_{random.randint(1000, 9999)}"
        }
    except Exception as e:
        print(f"API调用出错详情: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"API调用出错: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exhibit/<category>')
def exhibit(category):
    if category in museum_exhibits:
        return render_template('exhibit.html', category=category, exhibit=museum_exhibits[category])
    return "展品不存在", 404

@app.route('/dialog/<item_id>')
def dialog(item_id):
    if item_id in historical_figures:
        figure = historical_figures[item_id]
        # 找到对应的展品信息
        item_info = None
        category_name = ""
        for category, data in museum_exhibits.items():
            for item in data["exhibit_items"]:
                if item["id"] == item_id:
                    item_info = item
                    category_name = data["name"]
                    break
            if item_info:
                break
                
        return render_template(
            'dialog.html', 
            figure=figure, 
            item=item_info, 
            category=category_name,
            user_roles=user_roles,
            scenarios=historical_scenarios.get(item_id, []),
            historical_figures=historical_figures
        )
    return "历史人物不存在", 404

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    exhibit_context = data.get('exhibit', '')
    
    # 构建发送给模型的消息
    prompt = f"关于{exhibit_context}展品的问题: {user_message}"
    
    try:
        # 调用Together API
        response = call_together_api(prompt, session.get('conversation_id'))
        
        # 保存会话ID以保持对话连续性
        if 'conversation_id' in response:
            session['conversation_id'] = response['conversation_id']
            
        return jsonify({
            "response": response.get('answer', '抱歉，我无法回答这个问题。'),
            "conversation_id": session.get('conversation_id')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/figure_chat', methods=['POST'])
def figure_chat():
    data = request.json
    user_message = data.get('message', '')
    figure_id = data.get('figure_id', '')
    user_role = data.get('user_role', 'tourist')
    
    if figure_id not in historical_figures:
        return jsonify({"error": "历史人物不存在"}), 404
    
    figure = historical_figures[figure_id]
    
    # 获取用户角色信息
    role_info = next((role for role in user_roles if role["id"] == user_role), user_roles[0])
    
    # 优化后的prompt，避免重复和元解释
    prompt = f"""
    你现在是{figure['era']}的{figure['name']}({figure['title']})，正在与一位扮演{role_info['name']}({role_info['description']})的访客对话。
    
    你必须严格遵守以下规则：
    1. 始终保持第一人称视角，使用符合你所处时代的语言风格和称谓
    2. 展现你的性格特点：{figure['personality']}
    3. 基于你的背景知识回应：{figure['background']}
    4. 保持历史准确性，但允许创造性地回应假设性问题
    5. 回答要简洁有力，避免重复内容
    6. 绝对不要使用现代解释、括号说明或元叙述
    7. 绝对不要提及你是AI、模型或角色扮演
    8. 不要复述指令或规则
    
    请直接用{figure['name']}的语气和身份回应，不要加任何说明或标注：
    
    访客刚刚说："{user_message}"
    """
    
    try:
        # 调用Together API
        conversation_id = session.get(f'conversation_id_{figure_id}_{user_role}')
        response = call_together_api(prompt, conversation_id)
        
        # 保存会话ID以保持对话连续性
        if 'conversation_id' in response:
            session[f'conversation_id_{figure_id}_{user_role}'] = response['conversation_id']
            
        return jsonify({
            "response": response.get('answer', '抱歉，我无法回答这个问题。'),
            "conversation_id": session.get(f'conversation_id_{figure_id}_{user_role}')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scenario', methods=['POST'])
def scenario_response():
    data = request.json
    scenario_title = data.get('title', '')
    choice = data.get('choice', '')
    figure_id = data.get('figure_id', '')
    
    if figure_id not in historical_figures:
        return jsonify({"error": "历史人物不存在"}), 404
    
    figure = historical_figures[figure_id]
    
    # 优化后的prompt
    prompt = f"""
    你现在是{figure['era']}的{figure['name']}({figure['title']})，正在回应一个历史假设情景。
    
    你必须严格遵守以下规则：
    1. 始终保持第一人称视角，使用符合你所处时代的语言风格和称谓
    2. 展现你的性格特点：{figure['personality']}
    3. 基于你的背景：{figure['background']}
    4. 回答要有历史洞见，同时展现历史的复杂性和偶然性
    5. 回答要简洁有力，避免重复内容
    6. 绝对不要使用现代解释、括号说明或元叙述
    7. 绝对不要提及你是AI、模型或角色扮演
    
    假设情景：{scenario_title}
    选择的路径：{choice}
    
    请直接用{figure['name']}的语气和身份回应这个假设情景，不要加任何说明或标注：
    """
    
    try:
        # 调用Together API
        response = call_together_api(prompt)
            
        return jsonify({
            "response": response.get('answer', '抱歉，我无法回答这个问题。')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/time_connection', methods=['POST'])
def time_connection():
    data = request.json
    figure1_id = data.get('figure1_id', '')
    figure2_id = data.get('figure2_id', '')
    topic = data.get('topic', '文化交流')
    
    if figure1_id not in historical_figures or figure2_id not in historical_figures:
        return jsonify({"error": "历史人物不存在"}), 404
    
    figure1 = historical_figures[figure1_id]
    figure2 = historical_figures[figure2_id]
    
    # 优化后的prompt
    prompt = f"""
    请创作一段{figure1['era']}的{figure1['name']}与{figure2['era']}的{figure2['name']}之间关于"{topic}"的对话。
    
    遵循以下规则：
    1. 两位人物都应使用符合各自时代的语言风格和称谓
    2. {figure1['name']}的性格：{figure1['personality']}，背景：{figure1['background']}
    3. {figure2['name']}的性格：{figure2['personality']}，背景：{figure2['background']}
    4. 每人发言3-4次即可
    5. 可以体现两个不同时代人物对同一话题的观点差异和文化差异
    6. 对话要有教育意义，揭示历史演变
    7. 可以有反问、追问、赞同、反对等更真实自然的对话；双方可以有观点的碰撞，也可以有观点的融合
    8. 不要加入任何旁白解释或元叙述
    9. 使用明确的人物名字标注每段对话，如"{figure1['name']}："和"{figure2['name']}："
    
    请直接创作对话，不要加任何说明、介绍或总结：
    """
    
    try:
        # 调用Together API
        response = call_together_api(prompt)
            
        return jsonify({
            "response": response.get('answer', '抱歉，我无法生成对话。')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 