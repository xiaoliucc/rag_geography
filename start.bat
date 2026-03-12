@echo off
chcp 65001 >nul
echo ========================================
echo   高中地理 RAG 系统 - 快速启动
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查 Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 20+
    pause
    exit /b 1
)

echo [1/4] 检查依赖...
echo.

REM 后端依赖
if not exist "backend\venv" (
    echo 创建后端虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

echo 激活后端虚拟环境并安装依赖...
cd backend
call venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cd ..

echo.

REM 前端依赖
cd frontend
if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install --registry=https://registry.npmmirror.com
)
cd ..

echo.
echo ========================================
echo   启动服务...
echo ========================================
echo.
echo 后端将运行在: http://localhost:8000
echo 前端将运行在: http://localhost:5173
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动后端（新窗口）
start "RAG 后端" cmd /k "cd backend && venv\Scripts\activate && uvicorn api:app --reload --host 0.0.0.0 --port 8000"

REM 等待一下
timeout /t 3 /nobreak >nul

REM 启动前端（新窗口）
start "RAG 前端" cmd /k "cd frontend && npm run dev"

echo.
echo 服务正在启动中...
echo 请稍等几秒钟，然后打开浏览器访问
echo.
pause
