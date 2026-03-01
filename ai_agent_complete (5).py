import time
import requests
import urllib.parse
import json
import os
import platform

# ===================== 配置（替换成你的API Key）=====================
API_KEY = "sk-7df5fdcb15a94b73a1538359203aa384"

# ===================== 颜色配置 =====================
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'  # 新增灰色定义
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    # 背景色
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'

# 清理屏幕函数
def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

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

# ===================== 精准调用API =====================
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
        res = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30,
            verify=False
        )
        res.raise_for_status()
        result = json.loads(res.content.decode('utf-8'))
        return result["output"]["text"].strip()
    except Exception as e:
        err_info = f"{Colors.RED}错误：{str(e)}{Colors.RESET}"
        if 'res' in locals():
            err_info += f" | 响应：{res.content.decode('utf-8', errors='ignore')[:100]}"
        return err_info

# ===================== 界面美化函数 =====================
def print_banner():
    """打印欢迎横幅"""
    banner = f"""
{Colors.BG_PURPLE}{Colors.WHITE}{Colors.BOLD}
╔══════════════════════════════════════════════╗
║                ✨ AA酱的聊天小屋 ✨          ║
╠══════════════════════════════════════════════╣
║  📝 输入 计算+表达式 进行数学计算            ║
║  📝 输入 转小写+"文本" 转换文本为小写        ║
║  📝 输入 exit/quit/bye 退出程序              ║
║  💖 傲娇的AA酱随时为你解答各种问题～         ║
╚══════════════════════════════════════════════╝
{Colors.RESET}
    """
    print(banner)

def print_typing_animation():
    """打字机效果动画"""
    import sys
    typing_text = f"{Colors.CYAN}AA酱正在思考中...{Colors.RESET}"
    for char in typing_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)
    print()

def format_input_prompt():
    """格式化输入提示"""
    return f"{Colors.BLUE}{Colors.BOLD}你问：{Colors.RESET}    "

def format_output_prompt():
    """格式化输出提示"""
    return f"{Colors.PURPLE}{Colors.BOLD}AA酱：{Colors.RESET}    "

def print_separator():
    """打印分隔线"""
    print(f"{Colors.YELLOW}──────────────────────────────────────────{Colors.RESET}")

# ===================== 主程序 =====================
if __name__ == "__main__":
    # 自动安装 requests
    try:
        import requests
    except ImportError:
        print(f"{Colors.YELLOW}正在安装 requests（仅需1次）...{Colors.RESET}")
        import subprocess
        subprocess.check_call(["pip", "install", "requests", "-i", "https://mirrors.aliyun.com/pypi/simple/", "-q"])
        import requests
        requests.packages.urllib3.disable_warnings()

    # 清理屏幕并显示欢迎界面
    clear_screen()
    print_banner()
    
    # 欢迎语动画
    welcome_text = f"{Colors.GREEN}欢迎来到AA酱的聊天小屋～才...才不是特意等你的呢！{Colors.RESET}"
    for char in welcome_text:
        print(char, end='', flush=True)
        time.sleep(0.03)
    print("\n")
    print_separator()
    print()

    while True:
        try:
            # 获取用户输入
            q = input(format_input_prompt()).strip()
            
            # 退出条件
            if q.lower() in ["exit", "quit", "bye", "拜拜", "退出"]:
                print(f"\n{format_output_prompt()}{Colors.RED}再...再见！才不会想你的呢～{Colors.RESET}")
                print_separator()
                break
            
            # 空输入处理
            if not q:
                print(f"{format_output_prompt()}{Colors.RED}哼！你到底想说什么？{Colors.RESET}\n")
                continue
            
            start = time.time()
            
            # 显示思考动画
            print_typing_animation()
            
            # 处理不同类型的请求
            if "计算" in q:
                ans = calc(q)
            elif "小写" in q or "转小写" in q:
                ans = to_lower(q)
            else:
                ans = ai_ask(q)
            
            # 显示结果
            print(f"\n{format_output_prompt()}{ans}")
            # 显示耗时（修复了GRAY属性问题）
            print(f"{Colors.GRAY}耗时：{round(time.time()-start,2)}秒{Colors.RESET}")
            print_separator()
            print()
            
        except KeyboardInterrupt:
            # 处理Ctrl+C中断
            print(f"\n\n{format_output_prompt()}{Colors.RED}突...突然打断人家，很没礼貌的！{Colors.RESET}")
            print_separator()
            break
        except Exception as e:
            print(f"\n{format_output_prompt()}{Colors.RED}出错了：{str(e)}{Colors.RESET}\n")
            print_separator()