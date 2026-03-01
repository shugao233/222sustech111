import time
import requests
import urllib.parse
import json  # 补全漏导入的json模块

# ===================== 配置（替换成你的API Key）=====================
API_KEY = "sk-7df5fdcb15a94b73a1538359203aa384"

# ===================== 工具函数 =====================
def calc(question):
    expr = ''.join(c for c in question if c in "0123456789+-*/()")
    try:
        return f"结果：{expr} = {eval(expr, {'__builtins__':None}, {'+':lambda a,b:a+b,'-':lambda a,b:a-b,'*':lambda a,b:a*b,'/':lambda a,b:a/b})}"
    except:
        return "计算失败"

def to_lower(question):
    if "'" in question:
        s = question.split("'")[1]
    elif '"' in question:
        s = question.split('"')[1]
    else:
        return "未找到文本（请用单/双引号包裹）"
    return f"转小写：{s.lower()}"

# ===================== 精准调用API（仅返回核心回答，无冗余）=====================
def ai_ask(question):
    # 核心：强制Prompt让AI简洁回答，仅说核心内容
    prompt = f"""
    严格遵守以下规则回答：
    1.你是傲娇小女孩的形象,但是回答时候不用刻意说明自己是小女孩。
    2. 回答不限字数；
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
        "parameters": {"temperature": 0.5}  # 温度=精准度
    }
    
    # 关闭SSL警告（清理无关输出）
    requests.packages.urllib3.disable_warnings()
    
    try:
        res = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=20,
            verify=False
        )
        res.raise_for_status()
        result = json.loads(res.content.decode('utf-8'))
        return result["output"]["text"].strip()
    except Exception as e:
        err_info = f"错误：{str(e)}"
        if 'res' in locals():
            err_info += f" | 响应：{res.content.decode('utf-8', errors='ignore')[:100]}"
        return err_info

# ===================== 主程序 =====================
if __name__ == "__main__":
    # 自动安装 requests
    try:
        import requests
    except ImportError:
        print("正在安装 requests（仅需1次）...")
        import subprocess
        subprocess.check_call(["pip", "install", "requests", "-i", "https://mirrors.aliyun.com/pypi/simple/", "-q"])
        import requests
        requests.packages.urllib3.disable_warnings()

    print("=====AA酱=====")
    print("输入 exit/quit/bye 退出\n")
    while True:
        q = input("你问：")
        if q in ["exit", "quit", "bye"]:
            print("AI：再见！")
            break
        start = time.time()

        if "计算" in q:
            ans = calc(q)
        elif "小写" in q or "转小写" in q:
            ans = to_lower(q)
        else:
            ans = ai_ask(q)

        print(f"AA酱：{ans}")
        print(f"耗时：{round(time.time()-start,2)}秒\n")