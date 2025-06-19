# 🚀 项目启动指南

## 快速启动

### 方式一：一键启动（推荐）

```bash
# 在项目根目录执行
./start_mvc_game.sh
```

这个脚本会自动：
- 检查并创建conda环境
- 安装所有依赖
- 启动MVC架构后端（端口8001）
- 启动前端（端口5173）
- 自动配置API地址

### 方式二：手动启动

#### 1. 启动后端

```bash
cd backend
python start_mvc_app.py
```

#### 2. 启动前端

```bash
cd frontend  # 或 react_repo
npm install
npm run dev
```

## 🌐 访问地址

启动成功后，可以访问以下地址：

- **前端游戏**: http://localhost:5173
- **后端API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs
- **ReDoc文档**: http://localhost:8001/redoc
- **健康检查**: http://localhost:8001/health

## 📋 环境要求

- Python 3.8+
- Node.js 16+
- Conda（推荐）或 pip
- npm 或 yarn

## 🔧 故障排除

### 1. 端口被占用
如果8001或5173端口被占用，可以：
- 停止占用端口的进程
- 或修改配置文件中的端口号

### 2. 依赖安装失败
```bash
# 清理并重新安装
pip uninstall -r backend/requirements.txt
pip install -r backend/requirements.txt
```

### 3. 前端API连接失败
检查前端配置文件中的API地址是否正确：
```bash
# 检查前端环境变量
cat frontend/.env.local
```

## 📊 日志文件

- **后端日志**: `backend_mvc.log`
- **详细日志**: `backend/src/logs/` 目录下

## 🆘 获取帮助

- 查看API文档：http://localhost:8001/docs
- 查看项目README：`backend/README_MVC.md`
- 检查日志文件排查问题 