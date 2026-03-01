import time
import requests
import urllib.parse
import json
import os
import platform
import ast
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random  # 新增：用于随机动画
import glob  # 新增：用于查找本地图片

app = Flask(__name__)
CORS(app)

# ===================== 配置 =====================
API_KEY = "sk-7df5fdcb15a94b73a1538359203aa384"  # 替换为真实阿里云API Key
# 生图API配置（阿里云通义生图）
IMAGE_API_KEY = "sk-7df5fdcb15a94b73a1538359203aa384"  # 替换为实际生图API Key
chat_history = []
last_answer = ""

# ===================== 角色图片缓存 =====================
# 存储不同表情的角色图片URL
character_image_cache = {
    "idle": None,
    "shy": None,
    "angry": None,
    "think": None,
    "happy": None,
    "cry": None,
    "surprised": None,
    "tired": None
}

# 角色图片提示词（描述不同表情的可爱小女孩）
character_prompts = {
    "idle": "一个可爱的动漫风格小女孩，黑色头发，大眼睛，甜美微笑，自然站立，简洁背景",
    "shy": "一个可爱的动漫风格小女孩，黑色头发，大眼睛，脸红害羞，扭捏不安，简洁背景",
    "angry": "一个可爱的动漫风格小女孩，黑色头发，生气表情，眉毛竖起，鼓起腮帮，简洁背景",
    "think": "一个可爱的动漫风格小女孩，黑色头发，思考表情，轻轻眨眼，手指下巴，简洁背景",
    "happy": "一个可爱的动漫风格小女孩，黑色头发，开朗笑容，大眼睛眯成月牙，非常开心，简洁背景",
    "cry": "一个可爱的动漫风格小女孩，黑色头发哭泣，流眼泪，委屈表情，我见犹怜，简洁背景",
    "surprised": "一个可爱的动漫风格小女孩，黑色头发，惊讶表情，圆圆的大眼睛，小嘴张开，简洁背景",
    "tired": "一个可爱的动漫风格小女孩，黑色头发，没精神，疲惫困倦，半闭眼睛，无精打采，简洁背景"
}

# ===================== 颜色/工具函数 =====================
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'

def calc(question):
    expr = ''.join(c for c in question if c in "0123456789+-*/().")
    if not expr:
        return "未检测到有效计算表达式（支持 +-*/() ，例：计算1+2*(3-4)）"
    try:
        node = ast.parse(expr, mode='eval')
        allowed_nodes = (ast.Expression, ast.BinOp, ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.UnaryOp, ast.USub, ast.Constant)
        for n in ast.walk(node):
            if not isinstance(n, allowed_nodes):
                return "不支持的表达式（仅允许数字和+-*/()）"
        result = eval(compile(node, '<string>', 'eval'), {'__builtins__': None})
        return f"结果：{expr} = {result}"
    except SyntaxError:
        return "表达式语法错误（例：计算1+2*3）"
    except ZeroDivisionError:
        return "计算错误：除数不能为0"
    except Exception as e:
        return f"计算失败：{str(e)}"

def to_lower(question):
    if "'" in question:
        s = question.split("'")[1]
    elif '"' in question:
        s = question.split('"')[1]
    else:
        return "未找到文本（请用单/双引号包裹，例：转小写\"HELLO\"）"
    return f"转小写：{s.lower()}"

# ===================== AI对话核心 =====================
def ai_ask(question):
    prompt = f"""
    严格遵守以下规则回答：
    1.你是傲娇小女孩的形象,但是回答时候不用刻意说明自己是小女孩。
    2. 回答不限字数,但是不要拓展太多；
    3. 纯中文回答。
    4.回答的时候，表面上态度强硬内心柔软的性格特征表现为对关心自己的人故意冷淡甚至挑衅实则非常在意对方感受说话时常用反话掩饰真实情感在亲密关系中容易表现出矛盾行为既想靠近又害怕受伤常常通过否认和抗拒来表达喜欢会因为对方的关心而害羞但又不愿直接承认内心其实充满温柔和依赖感对外界保持一定距离但对特定对象会逐渐卸下防备言行举止中透露出一种独特的魅力和可爱之处。
    问题：{question}
    """
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": prompt}]},
        "parameters": {"temperature": 0.5}
    }
    requests.packages.urllib3.disable_warnings()
    try:
        res = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
        res.raise_for_status()
        result = json.loads(res.content.decode('utf-8'))
        answer = result["output"]["text"].strip()
        chat_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "answer": answer
        })
        return answer
    except Exception as e:
        err_info = f"错误：{str(e)}"
        if 'res' in locals():
            err_info += f" | 响应：{res.content.decode('utf-8', errors='ignore')[:100]}"
        return err_info

# ===================== 动画匹配核心（增强版） =====================
def get_animation(question, answer):
    # 合并问题和回答，双向匹配关键词
    full_text = (question + " " + answer).lower()
    
    # 扩展关键词库
    animation_rules = {
        "shy": ['喜欢', '想你', '关心', '爱', '脸红', '不好意思', '害羞', '心动'],
        "angry": ['生气', '讨厌', '烦', '怒', '滚', '不理你', '气死', '讨厌鬼'],
        "think": ['计算', '数学', '为什么', '怎么', '思考', '想想', '分析', '算一下'],
        "happy": ['开心', '笑', '好', '哈哈哈', '快乐', '高兴', '美滋滋', '开心果'],
        "cry": ['哭', '流眼泪', '难过', '伤心', '委屈', '呜呜', '哭唧唧', '心疼'],
        "surprised": ['惊讶', '哇', '天呐', '居然', '没想到', '震惊', '惊呆'],
        "tired": ['累', '疲惫', '困', '想睡', '没精神', '乏力', '歇会']
    }
    
    # 优先匹配关键词
    for anim, keywords in animation_rules.items():
        if any(word in full_text for word in keywords):
            return anim
    
    # 无匹配时随机切换基础动画
    idle_animations = ["idle", "think", "happy"]  # 基础动画池
    return random.choice(idle_animations)

# ===================== Flask接口 =====================
@app.route('/api/chat', methods=['POST'])
def chat():
    global last_answer
    data = request.get_json()
    question = data.get('question', '').strip()
    
    # 处理对话逻辑
    if not question:
        ans = "哼！你到底想说什么？"
    elif "计算" in question:
        ans = calc(question)
    elif "小写" in question or "转小写" in question:
        ans = to_lower(question)
    elif question.lower() == "历史":
        ans = json.dumps(chat_history, ensure_ascii=False)
    else:
        ans = ai_ask(question)
    
    # 获取增强版动画类型
    animation_type = get_animation(question, ans)
    last_answer = ans if not ans.startswith("错误") else ""
    
    return jsonify({
        "answer": ans,
        "animation": animation_type,
        "time": round(time.time(), 2)
    })

# 新增：获取角色图片接口
@app.route('/api/get-character-image', methods=['GET'])
def get_character_image():
    """
    获取指定表情的角色图片（本地随机，严格与resource下文件夹名对应）
    """
    print(f"[DEBUG] get_character_image called")
    animation_type = request.args.get('type', 'idle')
    print(f"[DEBUG] animation_type: {animation_type}")
    
    # 只允许严格匹配 resource 下的文件夹
    folder_path = os.path.join('resource', animation_type)
    if not os.path.isdir(folder_path):
        return jsonify({
            "error": f"未找到资源文件夹: resource/{animation_type}",
            "image_url": "",
            "animation": animation_type,
            "time": round(time.time(), 2)
        }), 404
    
    pattern = os.path.join(folder_path, '*')
    image_files = [f for f in glob.glob(pattern) if os.path.isfile(f) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    if not image_files:
        return jsonify({
            "error": f"本地没有找到{animation_type}类型的图片！",
            "image_url": "",
            "animation": animation_type,
            "time": round(time.time(), 2)
        }), 404
    
    # 随机选一张
    image_path = random.choice(image_files)
    rel_path = os.path.relpath(image_path, '.')
    url_path = rel_path.replace('\\', '/').replace(' ', '%20')
    
    return jsonify({
        "image_url": url_path,
        "animation": animation_type,
        "cached": False,
        "time": round(time.time(), 2)
    })

# 静态文件服务（如 resource 目录图片）
@app.route('/resource/<path:filename>')
def serve_resource(filename):
    return send_from_directory('resource', filename)

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(chat_history)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
