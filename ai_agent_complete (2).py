"""
通义千问 Agent 极简版：零编译依赖 + 无需numpy + 直接运行
核心：仅依赖 dashscope 纯Python SDK，无任何编译操作
"""
import time
import json
import urllib.request

# ===================== 无需pip安装，直接调用通义千问API（纯原生）=====================
def call_qwen_api_direct(question: str, api_key: str) -> str:
    """纯原生Python调用通义千问API，无需任何第三方SDK"""
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-turbo",
        "input": {
            "messages": [{"role": "user", "content": question}]
        },
        "parameters": {"temperature": 0.0}
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["output"]["text"].strip()
    except Exception as e:
        return f"回答失败：{str(e)}"

# ===================== 核心工具函数（纯Python，无依赖）=====================
def calculate(question: str) -> str:
    expr = ''.join([c for c in question if c in "0123456789+-*/()"])
    try:
        result = eval(expr, {"__builtins__": None}, {"+":lambda a,b:a+b, "-":lambda a,b:a-b, "*":lambda a,b:a*b, "/":lambda a,b:a/b})
        return f"{expr} = {result}"
    except:
        return "计算错误"

def text_convert(question: str) -> str:
    text = question.split("'")[1] if "'" in question else question.split('"')[1] if '"' in question else ""
    return text.lower() if "小写" in question else text.upper() if "大写" in question else "文本错误"

def search(question: str) -> str:
    kb = {"ollama":"Ollama是本地大模型框架","通义千问":"阿里云大模型","python":"Python编程语言"}
    kw = question.replace("是什么","").replace("？","").strip().lower()
    return kb.get(kw, "无相关信息")

# ===================== 主程序 =====================
if __name__ == "__main__":
    print("===== 通义千问 Agent 极简版（零编译依赖）=====")
    # 替换为你的API Key
    API_KEY = "sk-7df5fdcb15a94b73a1538359203aa384"
    
    test_qs = ["计算 333+456*2", "把'Hello AI'转小写", "Chatgpt是什么？"]
    for idx, q in enumerate(test_qs, 1):
        print(f"\n=== 问题{idx}：{q} ===")
        start = time.time()
        if "计算" in q:
            ans = calculate(q)
        elif "转小写" in q or "转大写" in q:
            ans = text_convert(q)
        elif "是什么" in q:
            ans = search(q)
        else:
            ans = call_qwen_api_direct(q, API_KEY)
        print(f"✅ 回答：{ans}")
        print(f"⏳ 耗时：{round(time.time()-start,2)}秒")