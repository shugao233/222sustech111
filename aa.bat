@echo off
chcp 65001 >nul 2>&1  :: 强制UTF-8编码，支持中文显示
echo ==============================
D:\agent_Ai\python.exe D:\agent_Ai\ai_agent_complete.py  :: 补全py文件绝对路径
pause  :: 运行结束后不闪退，按任意键关闭